# -*- coding: utf-8 -*-

# Parameters that used by more than one module

import os

config_translation_url = "translation_url"
work_directory = '~/dell/'
parent_path = os.path.expanduser(work_directory)
svc_delimitor = "_"
svc_placeholder = "?"
api_offset = 50
file_config_name = "dell_config.yml"
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
service_ch_placeholder = "?"

datetime_str_format = '%Y-%m-%d %H:%M:%S'
date_str_format = "%s年%s月%s日"
date_str_format_search = "%Y-%m-%d"
hour_str_format = "%H小时%M分钟%S秒"

search_url = "/search?svctag="

dell_api_url = "https://api.dell.com/support/v2/assetinfo/warranty/tags.json?"
dell_support_url = "http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/"
translation_url = "https://raw.githubusercontent.com/liukun1016/DellWarranty/master/translation.yml"
mail_post_url = "https://api.mailgun.net/v3/sandbox37699e306f69436d8f89f81915ad9f0a.mailgun.org/messages"
mail_from = "戴尔保修查询 <postmaster@sandbox37699e306f69436d8f89f81915ad9f0a.mailgun.org>"
mail_to = "Hotmail <daierchaxun@hotmail.com>"
mail_cc = "Kun <liukun1016@gmail.com>"

db_host = "localhost"
db_user = "root"
db_pwd = "password"
db_name = "dellwarranty"
db_tb_dell_asset = "dell_asset"
db_tb_warranty = "warranty"
db_tb_dell_warranty = "dell_warranty"
