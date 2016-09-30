# -*- coding: utf-8 -*-

from svc_process import target_svctags_batch
from api_entity import api_entities_batch
from utility import read_file, get_current_time, parse_cmd_args, save_object_to_path, Logger, diff_two_time
from translate import translate_dell_warranty, update_dell_warranty_translation, verify_NA_translation
from email_job import send_email
from entity import DellAsset
from constant import svc_delimitor, file_config_name, existing_dell_asset_dir, search_url, job_mode_dell_asset, job_mode_update_svctag
import sys, traceback

reload(sys)
sys.setdefaultencoding('utf8')

required_arg_list = ['--parent_path=', '--svctag=', '--job_mode=']
subject_temp = "%s 时间%s 标签%s"

if __name__ == "__main__":
	logger = Logger()
	logger.info("Prepare arguments for a job")
	start_time = get_current_time()
	arguments = parse_cmd_args(sys.argv, required_arg_list)
	parent_path = arguments['parent_path']
	svctag = arguments['svctag']
	job_mode = arguments['job_mode']
	log_output_path = "%s/log/%s_%s_%s.txt" % (parent_path, job_mode, start_time, svctag)
	config = read_file(parent_path + file_config_name, isYML=True, isURL=False)
	if config is None:
		logger.error("Config %s parsed as None; job quits" % (parent_path + file_config_name))
		save_object_to_path(object_L=logger, output_path=log_output_path)
	else:
		svc_L = svctag.split(svc_delimitor)
		history_valid_svctag_path = parent_path + "valid_svctags.txt"
		dell_asset_path = existing_dell_asset_dir
		output_csv_path = parent_path + "%s_%s.csv" % (start_time, svctag)
		api_url = config['dell_api_url'] % config["dell_api_key"]
		transl_url = config["translation_url"]
		dell_support_url = config['dell_support_url']
		output_dell_asset_L = []
		api_dell_asset_L = []
		NA_dict = {}
		try:
			if job_mode == job_mode_dell_asset:
				subject = subject_temp % ('新的查询开始', start_time, svctag)
				send_email(subject=subject, text="请等待邮件结果", config=config)	
				target_svc_L, existing_svc_S = target_svctags_batch(svc_L, dell_support_url, dell_asset_path, history_valid_svctag_path, logger)
				# Use valid service tags to call Dell API, and parse JSON data into a list of DellAsset entities
				if len(target_svc_L) == 0:
					logger.info("No target service tag for this " + svctag)
				else:
					api_dell_asset_L = api_entities_batch(target_svc_L, api_url, logger)
					if len(api_dell_asset_L) > 0:
						output_dell_asset_L, NA_dict = translate_dell_warranty(transl_url, api_dell_asset_L, logger)
					else:
						logger.warn("======No data for Dell Asset from API call")
				if len(existing_svc_S) > 0:
					existing_dell_asset_L = DellAsset.parse_dell_asset_file_batch(dell_asset_path, existing_svc_S, logger)
					# Translate all Warranties of each DellAsset, and find those warranties without available translation
					updated_dell_asset_L, NA_dict2 = update_dell_warranty_translation(transl_url, existing_dell_asset_L, dell_asset_path, logger)
					output_dell_asset_L.extend(updated_dell_asset_L)
					NA_dict.update(NA_dict2)
				else:
					logger.warn("======No existing Dell Asset for service tag " + svctag)
				if verify_NA_translation(NA_dict, logger):
					logger.warn("Additional translation needed")					
				else:
					logger.info("No additional translation needed")
				if len(output_dell_asset_L) > 0:
					logger.info("~~~~~~~%s output results in total" % len(output_dell_asset_L))
					# Save output into the csv_path and also existing dell asset
					save_object_to_path(object_L=output_dell_asset_L, output_path=output_csv_path)
					logger.info("~~~~~~~Save output as existing dell assets")
				else:
					logger.warn("-------Output for this job is empty")
			elif job_mode == job_mode_update_svctag:
				subject = subject_temp % ('新的标签更新开始', start_time, svctag)
				target_svctags_batch(svc_L, dell_support_url, dell_asset_path, history_valid_svctag_path, logger, svc_job=True)
				send_email(subject=subject, text=logger, config=config)
		except Exception, e:
			logger.error(str(e))
			logger.error(traceback.format_exc())
		logger.info("FINISH>>>>>>>>>>>>>>>> main")
		additional_text = "总用时 %s\n总共 %s个结果" % (diff_two_time(start_time, get_current_time()), len(output_dell_asset_L))
		additional_text += "请打开链接: %s%s%s\n" % (config['host_url'], search_url, svctag)
		logger.info(additional_text)
		if logger.has_error:
			additional_text += "查询程序出现错误，请等待解决。"
		if job_mode == job_mode_dell_asset:
			save_object_to_path(object_L=logger, output_path=log_output_path)
			subject = subject_temp % ("[查询任务结束] ", get_current_time(), svctag)
			send_email(subject=subject, text=additional_text, config=config, cc_mode=logger.has_error, attachment_path_L=[log_output_path])
		elif job_mode == job_mode_update_svctag:
			pass

