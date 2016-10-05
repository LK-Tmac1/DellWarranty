# -*- coding: utf-8 -*-
import sys, yaml
from utility import read_file, save_object_to_path
from constant import service_ch_placeholder, history_DA_file_format
"""
reload(sys)
sys.setdefaultencoding('utf8')
"""
def filter_NA_translation(tran_dict):
	# Filter those services without available Chinese translation from the dict
	for k, v in tran_dict.items():
		if v is None or v == 'null' or len(v.encode('utf-8')) == 0:
			tran_dict.pop(k)
	return tran_dict

def reverse_NA_translation(NA_dict):
	# Given a dictonary that all keys are warranty service without translation, 
	# and values, are a service tag of this warranty, return a dictionary with 
	# the warranty as the value and the dell asset service tag as the key
	NA_dict_reverse = {}
	for k, v in NA_dict.items():
		if v not in NA_dict_reverse:
			NA_dict_reverse[v] = ""
		NA_dict_reverse[v] = NA_dict_reverse[v] + ", " + k
	return NA_dict_reverse

def verify_NA_translation(NA_dict, logger):
	if bool(NA_dict):
		NA_dict = reverse_NA_translation(NA_dict)
		for k, v in NA_dict.items():
			temp = str(k) + ": " + str(v)
			logger.info(yaml.safe_dump(temp, allow_unicode=True, default_flow_style=False))
			return True
	return False

def translate_dell_warranty(yml_url_path, dell_asset_L, logger):
	tran_dict = read_file(yml_url_path, isYML=True, isURL=True)
	tran_dict = filter_NA_translation(tran_dict)
	logger.info("Read translation")
	NA_dict = {}
	for dell_asset in dell_asset_L:
		for w in dell_asset.get_warranty():
			if w is not None and w.service_en is not None:
				if w.service_ch == service_ch_placeholder:
					if w.service_en in tran_dict:
						w.set_service_ch(tran_dict[w.service_en])
						dell_asset.is_translation_updated = True
					else:
						NA_dict[w.service_en] = dell_asset.svctag
			else:
				logger.warn("Warranty service name not valid for %s and \n%s" % (dell_asset.svctag, w))
	return dell_asset_L, NA_dict

def update_dell_warranty_translation(transl_url, dell_asset_L, dell_asset_path, logger):
	dell_asset_L, NA_dict = translate_dell_warranty(transl_url, dell_asset_L, logger)
	for dell_asset in dell_asset_L:
		if dell_asset.is_translation_updated:
			save_object_to_path([dell_asset], dell_asset_path + dell_asset.svctag + history_DA_file_format)
			logger.info("Update service translation of " + dell_asset.svctag)
	return dell_asset_L, NA_dict
