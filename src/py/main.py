# -*- coding: utf-8 -*-

from svc_process import target_svctags_batch
from api_entity import api_entities_batch
from utility import read_file, get_current_time, parse_cmd_args, save_object_to_path, Logger, delete_file, diff_two_time
from translate import translate_dell_warranty, update_dell_warranty_translation
from email_job import send_email, email_job_output_translation
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
				send_email(subject=subject, text=" ", config=config, cc_mode=True)	
				target_svc_L, existing_svc_S = target_svctags_batch(svc_L, dell_support_url, dell_asset_path, history_valid_svctag_path, logger)
				# Use valid service tags to call Dell API, and parse JSON data into a list of DellAsset entities
				if len(target_svc_L) == 0:
					logger.info("No target service tag for this " + svctag)
				else:
					api_dell_asset_L = api_entities_batch(target_svc_L, api_url, logger)
					if len(api_dell_asset_L) > 0:
						output_dell_asset_L, NA_dict = translate_dell_warranty(transl_url, api_dell_asset_L, logger)
					else:
						logger.warn("=======No data for Dell Asset from API call")
				if len(existing_svc_S) > 0:
					existing_dell_asset_L = DellAsset.parse_dell_asset_file_batch(dell_asset_path, existing_svc_S, logger)
					# Translate all Warranties of each DellAsset, and find those warranties without available translation
					updated_dell_asset_L, NA_dict2 = update_dell_warranty_translation(transl_url, existing_dell_asset_L, dell_asset_path, logger)
					output_dell_asset_L.extend(updated_dell_asset_L)
					NA_dict.update(NA_dict2)
				else:
					logger.info("No existing Dell Asset for service tag " + svctag)
				if not bool(NA_dict):
					logger.info("No additional translation needed")
				else:
					logger.warn("Additional translation needed")
				if len(output_dell_asset_L) > 0:
					logger.info("~~~~~~~%s output results in total" % len(output_dell_asset_L))
					# Save output into the csv_path and also existing dell asset
					save_object_to_path(object_L=output_dell_asset_L, output_path=output_csv_path)
					logger.info("~~~~~~~Save output as existing dell asset")
					DellAsset.save_dell_asset_to_file(output_dell_asset_L, dell_asset_path, logger)
					# Email the csv output and also all NA translation
					additional_text = "总用时 %s\n总共 %s个结果" % (diff_two_time(start_time, get_current_time()), len(output_dell_asset_L))
					additional_text += "\n请打开链接: %s%s%s" % (config['host_url'], search_url, svctag)
					if email_job_output_translation(svctag=svctag, config=config, csv_path=output_csv_path, NA_dict=NA_dict, additional_text=additional_text):
						logger.info("Sending output email done")
					else:
						logger.error("Sending output email failed")
				else:
					logger.info("-------Output for this job is empty")
					send_email(subject='查询的标签 %s 没找到任何结果' % svctag, text=" ", config=config)
			elif job_mode == job_mode_update_svctag:
				subject = subject_temp % ('新的标签更新开始', start_time, svctag)
				target_svctags_batch(svc_L, dell_support_url, dell_asset_path, history_valid_svctag_path, logger, svc_job=True)
				send_email(subject=subject, text=logger, config=config, cc_mode=False)	
		except Exception, e:
			logger.error(str(e))
			logger.error(traceback.format_exc())
		logger.info("FINISH>>>>>>>>>>>>>>>> main")
		if logger.has_error:
			subject = subject_temp % ('查询结果失败', start_time, svctag)
			if job_mode == job_mode_dell_asset:
				send_email(subject=subject, text='程序运行出现错误，请等待解决.', config=config, cc_mode=True)
		else:
			subject = subject_temp % ('查询任务日志', start_time, svctag)
		logger.info('总用时 %s' % diff_two_time(start_time, get_current_time()))
		if job_mode == job_mode_dell_asset:
			save_object_to_path(object_L=logger, output_path=log_output_path)
			delete_file(output_csv_path)
			send_email(subject=subject, text=logger, config=config, cc_mode=False)
		elif job_mode == job_mode_update_svctag:
			print "~~~~~Final log:\n", logger

