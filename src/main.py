# -*- coding: utf-8 -*-
import sys
from backend.files import ZipFileSVC, FileUtility
from backend.mysql import InvalidHistoryClient
from backend.svctag import ServiceTagGenerator

# python main.py ABCEF?? verbose

parent_path = ""
history_zipfile = "./查询历史记录.zip"
config_yml = "./程序配置文件.yml"
excel_dir = "./Excel结果文件/"


def main(svc_input, verbose):
    """
    加载运行环境配置
    创建出所有可能查询码
    找到本地匹配的历史记录
    调用数据库，找到匹配的非法查询码历史
    根据历史，筛选出未知查询码
    调用戴尔查询API返回结果
    将JSON数据转化为实体类
    将实体类序列化到本地TXT文件以及Excel文档
    将序列化TXT文件存到本地历史记录
    更新数据库非法查询码历史
    发送邮件通知，结束程序，打印日志
    """
    configs = FileUtility.read_file(config_yml, isYML=True)
    svc_generator = ServiceTagGenerator(svc_input)
    history_zip = ZipFileSVC(zip_file_path=history_zipfile)
    mysql_invalid_client = InvalidHistoryClient()



    pass


if __name__ == '__main__':
    if len(sys.argv) == 0:
        print "需要7位查询保修码，比如ABCEF??，退出程序"
        sys.exit(-1)
    svc_input = sys.arg[0]
    verbose = len(sys.argv) > 1
    main(svc_input, verbose)
