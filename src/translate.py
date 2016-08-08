import yaml, os, requests, smtplib
from entity import DellAsset
from datetime import datetime
from email.mime.text import MIMEText


def read_translation_url(url_path):
	# Read input file and return a translation dictionary
	# With key as the service english and value as service chinese
	resp = requests.get(url_path)
	return yaml.load(resp.content)

def filter_translation(tran_dict):
	# Filter those services without available Chinese translation from the dict
	for k, v in tran_dict.items():
		if v is None or v == 'null' or len(v.encode('utf-8')) == 0:
			tran_dict.pop(k)
	return tran_dict

def add_translation_NA(dell_asset, NA_dict):
	# Given a DellAsset, if there is any warranty without available translation,
	# i.e. None or 'null' or empty, return a dictionary with the service name of 
	# the warranty as the key and the dell asset service tag as the value
	NA_dict = {} if NA_dict is None else NA_dict
	for w in dell_asset.get_warranty():
		if w.service_ch is None or w.service_ch == 'null':
			NA_dict[w.service_en] = dell_asset.svctag
	return NA_dict

def email_NA_translation(NA_dict, mail_from, mail_to, mail_api_key, mail_post_url):
	# Given a list of DellAsset object, find all those warranties without
	# available translation in Chinese, and send them to a given email address
	data = {"from": mail_from,
			"to": mail_to,
			"subject": "Translation request on " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
			"text": yaml.safe_dump(NA_dict, allow_unicode=True, default_flow_style=False) }
	return requests.post(mail_post_url, auth=("api", mail_api_key), data=data)
