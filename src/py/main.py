import yaml, requests
from svctag_process import valid_svctags_batch
from json_process import get_entities_batch
from utility import load_yaml_config, get_current_time, send_email
from translate import translate_dell_warranty

config_path = "/Users/kunliu/Desktop/work/dell_config.yml"

def main(suffix, digit, password):
	config = load_yaml_config(config_path)
	
	if password != config['password']:
		return 1
	if len(suffix) + int(digit) != 7:
		return 2

	csv_output_path = "/output/%s_%s" % (suffix, get_current_time())
	
	valid_svctag_L = valid_svctags_batch(suffix=suffix, dell_support_url=config["dell_support_url"], d=digit)

	url = config['dell_api_url'] % config["dell_api_key"]
	
	dell_entities_L = get_entities_batch(svctag_L=valid_svctag_L, url=url)
	
	transl_url = config["git_translate_url"]
	
	dell_asset_L, NA_dict = translate_dell_warranty(yml_url_path=transl_url, dell_asset_L=dell_entities_L)
	
	if save_entity_csv(dell_asset_L=dell_asset_L, output_path=csv_output_path):
		if email_csv_attachment(suffix=suffix, config=config, csv_path=csv_output_path, NA_dict=NA_dict):
			return 0
		else:
			send_email(subject="Send email error", text=csv_output_path, attachment_L=None, config=config)	
	else:
		send_email(subject="Save output error", text=csv_output_path, attachment_L=None, config=config)
	
	return 4

"""
L = valid_svctags_batch(suffix="3JR32", dell_support_url="http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/", d=2)

a = Warranty("2012-12-21T13:00:00", "2015-12-22T12:59:59", "Parts Only Warranty", "true","仅限部件保修(POW)")
b = Warranty("2011-01-21T13:00:00", "2012-01-12T12:59:59", "Next Business Day response", "true", "下个工作日送达")
c = Warranty("2014-01-21T13:00:00", "2016-11-22T12:59:59", "Parts Only Warranty (Carry-In Service)", "true","仅限部件保修(送修服务)")

d = DellAsset("XPS 13 L322X", "G3VG2W1", "2012-12-21T13:00:00", [a,b,c])
"""