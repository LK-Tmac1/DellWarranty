from svc_process import target_svctags_batch
from api_entity import api_entities_batch
from utility import read_file, get_current_time, parse_cmd_args, save_object_to_path, Logger
from translate import translate_dell_warranty, update_dell_warranty_translation
from email_job import send_email, email_job_output_translation
from entity import DellAsset
from constant import svc_delimitor, file_config_name
import sys

required_arg_list = ['--parent_path=', '--svctag=']

if __name__ == "__main__":
	logger = Logger()
	logger.info("Prepare arguments for a job")
	current_time = get_current_time()
	arguments = parse_cmd_args(sys.argv, required_arg_list)
	parent_path = arguments['parent_path']
	svctag = arguments['svctag']
	log_output_path = "%slog/%s_%s.txt" % (parent_path, current_time, svctag)
	config = read_file(parent_path + file_config_name, isYML=True, isURL=False)
	if config is None:
		logger.error("Config %s parsed as None; job quits" % (parent_path + file_config_name))
		save_object_to_path(object_L=logger, output_path=log_output_path)
	else:
		svc_L = svctag.split(svc_delimitor)
		history_valid_svctag_path = parent_path + "valid_svctags.txt"
		dell_asset_path = parent_path + "dell_asset/"
		output_csv_path = parent_path + "output/%s_%s.csv" % (current_time, svctag)
		api_url = config['dell_api_url'] % config["dell_api_key"]
		transl_url = config["translation_url"]
		dell_support_url = config['dell_support_url']
		output_dell_asset_L = []
		api_dell_asset_L = []
		NA_dict = {}
		try:
			subject = "%s_%s_%s" % (config['email_subject_new_job'], current_time, svctag)
			send_email(subject=subject, text=logger, config=config, cc_mode=False)	
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
				if bool(NA_dict):
					logger.info("No additional translation needed")
				else:
					logger.warn("Additional translation needed")
			else:
				logger.info("No existing Dell Asset for service tag " + svctag)
			if len(output_dell_asset_L) > 0:
				logger.info("~~~~~~~%s output results in total" % len(output_dell_asset_L))
				# Save output into the csv_path
				save_object_to_path(object_L=output_dell_asset_L, output_path=output_csv_path)
				# Email the csv output and also all NA translation
				if email_job_output_translation(svctag=svctag, config=config, csv_path=output_csv_path, NA_dict=NA_dict):
					logger.info("Sending email done")
				else:
					logger.error("Sending output email failed")
			else:
				logger.info("-------Output for this job is empty")
		except Exception, e:
			logger.error("Exception encountered when running the job:")
			logger.error(str(e))
		logger.info("FINISH>>>>>>>>>>>>>>>> main")
		save_object_to_path(object_L=logger, output_path=log_output_path)
		subject = 'email_subject_error' if logger.has_error else ('email_subject_warning' if logger.has_warn else 'email_subject_success')
		subject = "%s_%s_%s" % (config[subject], current_time, svctag)
		send_email(subject=subject, text=logger, config=config, cc_mode=False)	
