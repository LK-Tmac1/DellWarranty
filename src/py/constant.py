# -*- coding: utf-8 -*-

html_error_input = "error-input.html"
html_home = "home.html"
html_confirm_job = "confirm.html"

error_message = {
	1 : '密码输入不正确',
	2 : '服务标签输入不正确',
	3 : '测试用文件路径不存在，请勿改动'
}

error_exceed_quote = "Service Profile Throttle Limit Reached"
error_incorrect_tags = "The number of tags that returned no data exceeded the maximum percentage of incorrect tags"
error_internal_auth = "The request has failed due to an internal authorization configuration issue"
error_api_key = "User Identification failed in Key Management Service"
error_unknown = "Unknown error happened"

api_error_code = { 	
	-1 : error_unknown,
	1 : error_exceed_quote,
	2 : error_incorrect_tags,
	3 : error_internal_auth,
	4 : error_api_key }

api_json_l1 = "GetAssetWarrantyResponse"
api_json_l2 = "GetAssetWarrantyResult"

