# -*- coding: utf-8 -*-

import os, sys, traceback
from batch import Batch
from svctag import SVCGenerator, letters
from utility import DateTimeUtil, Logger, Email, FileUtil
from zip import ZipFileSVC
from entity import DellAsset
from windows import WindowsUtil, UnicodeStreamFilter

if sys.stdout.encoding == 'cp936':
    # 解决Windows系统下，命令行中文打印问题
    sys.stdout = UnicodeStreamFilter(sys.stdout)

# 加载运行环境配置
parent_path = os.getcwd() # current working dir
history_path = WindowsUtil.convert_win_path(os.path.join(parent_path, "lishi"))
history_zipfile = WindowsUtil.convert_win_path(os.path.join(history_path, "all.zip"))
temp_dir = WindowsUtil.convert_win_path(os.path.join(history_path, "temp"))
invalid_history_file_path = WindowsUtil.convert_win_path(os.path.join(history_path, "invalid.txt"))
config_yml_path = WindowsUtil.convert_win_path(os.path.join(history_path, "config.yml"))
excel_dir = WindowsUtil.convert_win_path(os.path.join(history_path, "excel"))


def main(svc_input, configs):
    logger = Logger("查询日志", verbose=True)
    log_file_name = "log%s_%s.txt" % (svc_input.replace("?", "#"), DateTimeUtil.get_current_datetime(is_date=True))
    log_file_path = WindowsUtil.convert_win_path(os.path.join(temp_dir, log_file_name))
    logger.info("[开始查询] %s" % svc_input)
    try:
        # 找到本地匹配的保修历史记录
        history_zip = ZipFileSVC(zip_file_path=history_zipfile, mode='a')
        start_time = DateTimeUtil.get_current_datetime()
        # 创建出所有可能查询码
        svc_generator = SVCGenerator(svc_input, logger)
        logger.info("创建出所有可能查询码：%s" % len(svc_generator.target_svc_set))
        # 根据本地匹配的非法查询码历史，筛选出目标查询码，以及非法查询码
        existed_svc = history_zip.find_file_regex(svc_generator.regex)
        svc_generator.generate_target_svc_batch(existed_svc, invalid_history_file_path)
        # 调用戴尔查询API，并将API数据转化为实体类数据
        output_dell_asset_list = list([])
        if svc_generator.target_svc_set:
            batch = Batch(logger, configs)
            api_dell_asset_list = batch.begin(svc_generator.target_svc_set)
            output_dell_asset_list = api_dell_asset_list
            logger.info("从API中总共得到%s个结果" % (len(api_dell_asset_list)))
            logger.info("将实体类序列化到本地临时TXT文件")
            temp_text_files_path = DellAsset.serialize_txt_batch(api_dell_asset_list, temp_dir)
            logger.info("将序列化临时文件存到本地zip历史记录，总数：%s" % len(temp_text_files_path))
            history_zip.add_new_file_batch(temp_text_files_path)
            logger.info("删除临时 %s 个TXT文件" % len(temp_text_files_path))
            for file_path in temp_text_files_path:
                FileUtil.delete_file(file_path)
            logger.info("将API得到的实体类和历史记录实体类合并")
        else:
            logger.warn("目标查询码为空，仅从从历史记录中导出结果")
        for svc in svc_generator.existed_svc_set:
            dell_asset_content = history_zip.get_member_content(file_name="%s.txt" % svc)
            output_dell_asset_list.append(DellAsset.deserialize_txt(dell_asset_content))
        logger.info("添加历史记录，总共得到%s个结果" % (len(output_dell_asset_list)))
        excel_output_path = WindowsUtil.convert_win_path(os.path.join(excel_dir, "%s.xlsx" % svc_generator.get_file_name()))
        DellAsset.save_as_excel_batch(output_dell_asset_list, excel_output_path)
        if FileUtil.is_path_existed(excel_output_path):
            logger.info("存为Excel文档成功")
            end_time = DateTimeUtil.get_current_datetime()
            logger.info("总用时 %s " % DateTimeUtil.datetime_diff(start_time, end_time))
            logger.info("[查询结束] 总共%s个结果 保存在：%s" % (len(output_dell_asset_list), excel_output_path))
        else:
            logger.error("[保存结果失败] %s" % excel_output_path)
    except Exception as e:
        # 若程序出现错误失败，发送邮件
        logger.error("[查询失败] 已发送报告 请等待解决")
        logger.error("%s\n%s" % (e, traceback.format_exc()))
        logger.save(log_file_path)
        email_api_key = configs["email_api_key"]
        email = Email(email_api_key, subject="[查询失败] %s %s" % (DateTimeUtil.get_current_datetime(is_date=True), svc_input))
        email.add_attachment(log_file_path)
        email.send(cc_mode=logger.has_error)


if __name__ == '__main__':
    while True:
        print "请输入7位查询码，未知位用?代替，比如ABCEF??（符号为英文符号）"
        required_file_path = [history_zipfile, config_yml_path, invalid_history_file_path]
        start = True
        for f in required_file_path:
            if not FileUtil.is_path_existed(f):
                print "请把程序运行文件放到程序运行文件夹下"
                start = False
                break
        if start:
            line = sys.stdin.readline()
            svc_input = line.split()[0]
            configs = FileUtil.read_file(config_yml_path, isYML=True)
            if len(svc_input) != 7:
                print "需要7位查询码"
            elif configs is None:
                print "请把正确的配置文件放到程序运行文件夹下"
            else:
                wild_card_count = 0
                for w in svc_input:
                    if w not in letters:
                        wild_card_count += 1
                if wild_card_count >= 4:
                    print "最多3位未知查询码，否则时间会过长"
                else:
                    main(svc_input, configs)
        print "==============================="
