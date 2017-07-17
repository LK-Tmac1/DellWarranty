# -*- coding: utf-8 -*-

import os
import sys
import traceback
from collections import deque

from batch import Batch
from svctag import SVCGenerator
from utility import DateTimeUtil, Logger, Email
from zip import ZipFileSVC, FileUtil

from entity import DellAsset

parent_path = "/Users/kunliu/Desktop/dell"
history_path = os.path.join(parent_path, "历史记录")
history_zipfile = os.path.join(history_path, "查询历史.zip")
temp_dir = os.path.join(history_path, "临时文件")
log_file_path = os.path.join(temp_dir, "查询日志.txt")
invalid_history_file_path = os.path.join(history_path, "非法查询码.txt")
config_yml = os.path.join(parent_path,"程序配置.yml")
excel_dir = os.path.join(parent_path, "Excel结果")


def main(svc_input):
    logger = Logger("查询日志", verbose=True)
    logger.info("[开始查询] %s" % svc_input)
    # 加载运行环境配置
    configs = FileUtil.read_file(config_yml, isYML=True)
    email_api_key = configs["email_api_key"]
    email = Email(email_api_key, subject="[查询任务结束] 标签 %s" % svc_input)
    try:
        # 找到本地匹配的保修历史记录
        history_zip = ZipFileSVC(zip_file_path=history_zipfile, mode='a')
        start_time = DateTimeUtil.get_current_datetime()
        # 创建出所有可能查询码
        svc_generator = SVCGenerator(svc_input, logger)
        logger.info("创建出所有可能查询码：%s" % svc_generator.target_svc_size())
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
        excel_output_path = os.path.join(excel_dir, "%s.xlsx" % svc_generator.get_file_name())
        DellAsset.save_as_excel_batch(output_dell_asset_list, excel_output_path)
        if FileUtil.is_path_existed(excel_output_path):
            logger.info("存为Excel文档成功")
            email.add_attachment(excel_output_path)
            end_time = DateTimeUtil.get_current_datetime()
            logger.info("总用时 %s " % DateTimeUtil.datetime_diff(start_time, end_time))
            logger.info("[查询结束] 总共%s个结果 保存在：%s" % (len(output_dell_asset_list), excel_output_path))
        else:
            logger.error("[保存结果失败] %s" % excel_output_path)
    except Exception as e:
        # 若程序出现错误失败
        logger.error("%s\n%s" % (e, traceback.format_exc()))
        email.update_subject("[查询失败] %s %s" % (DateTimeUtil.get_current_datetime(is_date=True), svc_input))
        logger.error("[查询失败] 已发送报告 请等待解决")
    finally:
        logger.info("发送邮件通知")
        FileUtil.save_object_to_path(logger, log_file_path)
        email.add_attachment(log_file_path)
        email.send(cc_mode=True)
        FileUtil.delete_file(log_file_path)


if __name__ == '__main__':
    # Example: python main.py ABCEF??
    arguments = deque(sys.argv)
    if arguments[0].find("main") >= 0:
        arguments.popleft()
    if len(arguments) == 0 or len(arguments[0]) != 7:
        print "需要7位查询保修码，比如ABCEF??"
    else:
        main(arguments.popleft())
