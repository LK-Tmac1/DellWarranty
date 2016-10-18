# -*- coding: utf-8 -*-

# Parameters that used by more than one module

import os

config_translation_url = "translation_url"
work_directory = '~/dell/'
parent_path = os.path.expanduser(work_directory)
existing_dell_asset_dir = parent_path + "existing_dell_asset/"
svc_delimitor = "_"
svc_placeholder = "?"
api_offset = 50
file_config_name = "dell_config.yml"
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
history_DA_file_format = '.txt'
service_ch_placeholder = "?"

datetime_str_format = '%Y-%m-%d %H:%M:%S'
date_str_format = "%s年%s月%s日"
date_str_format_search = "%Y-%m-%d"
hour_str_format = "%H小时%M分钟%S秒"

search_url = "/search?svctag="
job_mode_dell_asset = "dellasset"
job_mode_update_svctag = "svctag"
