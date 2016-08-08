import yaml, requests
from entity import DellAsset
from datetime import datetime


def read_translation_url(translate_url_path):
	# Read input file and return a translation dictionary
	# With key as the service english and value as service chinese
	resp = requests.get(translate_url_path)
	return yaml.load(resp.content)

def filter_NA_translation(tran_dict):
	# Filter those services without available Chinese translation from the dict
	for k, v in tran_dict.items():
		if v is None or v == 'null' or len(v.encode('utf-8')) == 0:
			tran_dict.pop(k)
	return tran_dict

def add_NA_translation(dell_asset, NA_dict):
	# Given a DellAsset, if there is any warranty without available translation,
	# i.e. None or 'null' or empty, return a dictionary with the service names of 
	# the warranty as the value and the dell asset service tag as the key
	NA_dict = {} if NA_dict is None else NA_dict
	for w in dell_asset.get_warranty():
		if w.service_ch is None or w.service_ch == 'null':
			NA_dict[w.service_en] = dell_asset.svctag
	NA_dict_reverse = {}
	for k, v in NA_dict.items():
		if v not in NA_dict_reverse:
			NA_dict_reverse[v] = ""
		NA_dict_reverse[v] = NA_dict_reverse[v] + ", " + k
	return NA_dict_reverse

def email_NA_translation(NA_dict, mail_from, mail_to, mail_api_key, mail_post_url):
	# Given a list of DellAsset object, find all those warranties without
	# available translation in Chinese, and send them to a given email address
	data = {"from": mail_from,
			"to": mail_to,
			"subject": "Translation request on " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
			"text": yaml.safe_dump(NA_dict, allow_unicode=True, default_flow_style=False) }
	return requests.post(mail_post_url, auth=("api", mail_api_key), data=data)

def update_NA_translation(csv_input_path, translate_url_path, csv_output_path):
	# Given a CSV file, update all the services translations based on the 
	# translate url path provided, and output another csv file
	return ""