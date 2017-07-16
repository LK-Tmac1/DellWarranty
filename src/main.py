# -*- coding: utf-8 -*-

import sys, os, traceback
from collections import deque
from backend.zip import ZipFileSVC, FileUtil
from backend.mysql import InvalidHistoryClient
from backend.svctag import SVCTagContainer
from backend.entity import DellAsset
from backend.utility import DateTimeUtil, Logger, Email
from backend.batch import Batch

parent_path = "/Users/kunliu/Desktop/dell"
history_zipfile = os.path.join(parent_path, "查询历史.zip")
config_yml = os.path.join(parent_path,"程序配置.yml")
excel_dir = os.path.join(parent_path, "temp")
temp_dir = os.path.join(parent_path, "临时文件")


def main(arguments):
    svc_input = arguments[0]
    logger = Logger("查询日志", verbose=True)
    logger.info("[开始查询] %s" % svc_input)
    # 加载运行环境配置
    configs = FileUtil.read_file(config_yml, isYML=True)
    email_api_key = configs["email_api_key"]
    email = Email(email_api_key, subject="[查询任务结束] 标签 %s" % svc_input)
    try:
        start_time = DateTimeUtil.get_current_datetime()
        # 创建出所有可能查询码
        svc_generator = SVCTagContainer(svc_input)
        logger.info("创建出所有可能查询码：%s" % svc_generator.svc_size())
        # 找到本地匹配的历史记录
        history_zip = ZipFileSVC(zip_file_path=history_zipfile)
        # 调用数据库，找到匹配的非法查询码历史
        # db_client = InvalidHistoryClient()
        # invalid_history = db_client.get_invalid_from_regex(svc_generator.regex)
        invalid_history = set([])
        logger.info("从数据库总找到匹配的非法查询码历史：%s" % len(invalid_history))
        # 根据历史，筛选出目标查询码，以及非法查询码
        svc_generator.filter_history(invalid_history)
        existed_svc = history_zip.find_file_regex(svc_generator.regex)
        svc_generator.split_existed(existed_svc)
        logger.info("已经存在的查询码历史：%s" % len(svc_generator.existed_svc_set))
        invalid_svc_list = svc_generator.remove_invalid_batch()
        logger.info("过滤掉非法的查询码：%s" % len(invalid_svc_list))
        logger.info("更新数据库非法查询码")
        # db_client.insert_invalid_batch(invalid_svc_list)
        # 调用戴尔查询API，并将API数据转化为实体类数据
        batch = Batch(logger, configs)
        api_dell_asset_list = batch.begin(svc_generator.target_svc_set)
        logger.info("从API中总共得到%s个结果" % (len(api_dell_asset_list)))
        logger.info("将实体类序列化到本地临时TXT文件")
        output_file_names = DellAsset.serialize_txt_batch(api_dell_asset_list, temp_dir)
        logger.info("将序列化临时文件存到本地zip历史记录，并删除临时文件")
        for file_name in output_file_names:
            history_zip.add_new_file_batch(os.path.join(temp_dir, file_name))
            FileUtil.delete_file(os.path.join(temp_dir, file_name))
        logger.info("将API得到的实体类和历史记录实体类合并，存为Excel文档")
        total = len(api_dell_asset_list)
        for svc in svc_generator.existed_svc_set:
            dell_asset_content = history_zip.get_member_content(file_name="%s.txt" % svc)
            api_dell_asset_list.append(DellAsset.deserialize_txt(dell_asset_content))
        logger.info("添加历史记录，总共得到%s个结果" % (len(api_dell_asset_list)))
        excel_output_path = os.path.join(excel_dir, "%s.xlsx" % svc_generator.get_output_name())
        DellAsset.save_as_excel_batch(api_dell_asset_list, excel_output_path)
        if FileUtil.is_path_existed(excel_output_path):
            logger.info("成功存到结果文件：%s" % excel_output_path)
            email.add_attachment(excel_output_path)
            end_time = DateTimeUtil.get_current_datetime()
            logger.info("总用时 %s " % DateTimeUtil.datetime_diff(start_time, end_time))
            logger.info("[查询结束] 总共%s个结果 存在%s" % (total, excel_output_path))
        else:
            logger.error("[保存结果失败] %s" % excel_output_path)
    except Exception as e:
        # 若程序出现错误失败
        logger.error("%s\n%s" % (e, traceback.format_exc()))
        email.update_subject("[查询失败] %s %s" % (DateTimeUtil.get_current_datetime(is_date=True), svc_input))
        logger.error("[查询失败] 已发送报告 请等待解决")
    finally:
        logger.info("发送邮件通知")
        if logger.has_error:
            email.add_text(logger.__repr__())
        email.send(cc_mode=logger.has_error)


if __name__ == '__main__':
    # Example: python main.py ABCEF??
    arguments = deque(sys.argv)
    if arguments[0].find("main") >= 0:
        arguments.popleft()
    arguments[0] = "ABCDEF?"
    if len(arguments) == 0 or len(arguments[0]) != 7:
        print "需要7位查询保修码，比如ABCEF??"
    else:
        main(arguments)
