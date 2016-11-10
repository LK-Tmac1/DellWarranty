# -*- coding: utf-8 -*-

# python main.py --parent_path=/Users/kunliu/dell/ --svctag=A_B_C_D_E_F_? --v=1

from svc_process import target_svctags_batch
from api_entity import api_entities_batch
from utility import read_file, get_current_datetime, parse_cmd_args, save_object_to_path, diff_two_datetime, \
	delete_file
from translate import translate_dell_warranty, update_dell_warranty_translation, verify_NA_translation
from email_job import send_email
from entity import DellAsset, Logger
from constant import svc_delimitor, file_config_name, existing_dell_asset_dir, \
	history_DA_file_format, config_translation_url
from excel import save_dell_asset_excel
import sys, traceback, socket


required_arg_list = ['--parent_path=', '--svctag=', '--v=']
subject_temp = "%s 时间%s 标签%s"

if __name__ == "__main__":
	arguments = parse_cmd_args(sys.argv, required_arg_list)
	parent_path = arguments['parent_path']
	svctag = arguments['svctag']
	verbose = True if 'v' in arguments else False
	logger = Logger(verbose)
	start_time = get_current_datetime()
	logger.info("Prepare arguments for a job on %s in machine: %s " % (start_time, socket.gethostname()))
	log_output_path = "%slog/dellasset_%s.txt" % (parent_path, svctag)
	config = read_file(parent_path + file_config_name, isYML=True, isURL=False)
	if config is None:
		logger.error("Config %s parsed as None; job quits" % (parent_path + file_config_name))
		save_object_to_path(value=logger, output_path=log_output_path)
	else:
		svc_L = svctag.split(svc_delimitor)
		history_valid_svctag_path = parent_path + "valid_svctags.txt"
		dell_asset_path = existing_dell_asset_dir
		search_history_path = parent_path + "search_history.yml"
		dell_asset_output_path = parent_path + "output_%s.xlsx" % svctag
		api_url = config['dell_api_url']
		api_key_L = config["dell_api_key"].values()
		transl_url = config[config_translation_url]
		dell_support_url = config['dell_support_url']
		output_dell_asset_L = []
		api_dell_asset_L = []
		NA_dict = {}
		additional_text = ""
		need_translation = False
		try:
			subject = subject_temp % ('新的查询开始', start_time, svctag)
			if not verbose:
				send_email(subject=subject, text="请等待邮件结果", config=config)
			logger.info("Send email to %s" % config['mail_to'])	
			target_svc_L, existing_svc_S = target_svctags_batch(svc_L, dell_support_url, dell_asset_path, history_valid_svctag_path, logger, search_history_path)
			# Use valid service tags to call Dell API, and parse JSON data into a list of DellAsset entities
			if len(target_svc_L) == 0:
				logger.warn("No target svctag needed for API call")
			else:
				api_dell_asset_L = api_entities_batch(target_svc_L, api_url, api_key_L, logger)
				if len(api_dell_asset_L) > 0:
					output_dell_asset_L, NA_dict = translate_dell_warranty(transl_url, api_dell_asset_L, logger)
				else:
					logger.warn("======No data for Dell Asset from previous API call")
			if len(existing_svc_S) > 0:
				existing_dell_asset_L = DellAsset.parse_dell_asset_file_batch(dell_asset_path, existing_svc_S, logger=logger)
				# Translate all Warranties of each DellAsset, and find those warranties without available translation
				updated_dell_asset_L, NA_dict2 = update_dell_warranty_translation(transl_url, existing_dell_asset_L, dell_asset_path, logger)
				output_dell_asset_L.extend(updated_dell_asset_L)
				NA_dict.update(NA_dict2)
			else:
				logger.warn("======No existing Dell Asset for service tag " + svctag)
			if verify_NA_translation(NA_dict, logger):
				logger.warn("查询结果存在保修需要翻译")
				need_translation = True
				additional_text += "查询结果存在保修需要翻译"
			else:
				logger.info("No additional translation needed")
			if len(output_dell_asset_L) > 0:
				logger.info("~~~~~~~%s output results in total" % len(output_dell_asset_L))
				# Save output into the csv_path and also existing dell asset
				logger.info("~~~~~~~Save output as existing dell assets")
				for da in output_dell_asset_L:
					if da is not None and da.svctag != "" and da.is_translation_updated:
						temp_path = existing_dell_asset_dir + da.svctag + history_DA_file_format
						save_object_to_path(value=da, output_path=temp_path)
				if save_dell_asset_excel(output_dell_asset_L, dell_asset_output_path):
					logger.info("保存结果到Excel文件 %s" % dell_asset_output_path)
				else:
					logger.error("保存Excel文件出错")
			else:
				logger.warn("-------Output for this job is empty")
		except Exception, e:
			logger.error(str(e))
			logger.error(traceback.format_exc())
		logger.info("\nFINISH\n")
		additional_text += "\n总用时 %s\n总共 %s个结果" % (diff_two_datetime(start_time, get_current_datetime()), len(output_dell_asset_L))
		logger.info(additional_text)
		subject = subject_temp % ("[查询任务结束] ", get_current_datetime(is_date=True), svctag)
		if logger.has_error:
			additional_text += "\n查询程序出现错误，请等待解决。"
		save_object_to_path(value=logger, output_path=log_output_path)
		if send_email(subject=subject, text=additional_text, config=config, cc_mode=logger.has_error or need_translation, attachment_path_L=[log_output_path, dell_asset_output_path]):
			logger.info("Send email to %s" % config['mail_to'])
		else:
			logger.error("Send email failed")
		save_object_to_path(value=logger, output_path=log_output_path)
		if not logger.has_error:
			delete_file(dell_asset_output_path)
