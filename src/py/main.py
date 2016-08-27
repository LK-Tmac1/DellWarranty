from svc_process import target_svctags_batch
from api_entity import api_entities_batch
from utility import read_file, get_current_time, parse_cmd_args, save_object_to_path, Logger
from translate import translate_dell_warranty
from email_job import send_email, email_job_output_translation
from entity.DellAsset import load_dell_asset
from constant import svc_delimitor, file_config_name
import traceback, sys

required_arg_list = ['--parent_path=', '--svctag=']

if __name__ == "__main__":
	# Prepare arguments for a job
	arguments = parse_cmd_args(sys.argv, required_arg_list)
	# """
	parent_path = arguments['parent_path']
	svctag = arguments['svctag']
	svc_L = svctag.split(svc_delimitor)
	config = read_file(parent_path + file_config_name, isYML=True, isURL=False)
	history_valid_svctag_path = parent_path + "valid_svctags.txt"
	dell_asset_path = parent_path + "dell_asset/"
	csv_output_path = parent_path + "output/"
	api_url = config['dell_api_url'] % config["dell_api_key"]
	transl_url = config["translation_url"]
	dell_support_url = config['dell_support_url']
	current_time = get_current_time()
	log_output_path = "%slog/%s__%s.txt" % (parent_path, current_time, svctag)
	logger = Logger()
	try:
		target_svc_L, existing_svc_S = target_svctags_batch(svc_L, dell_support_url, dell_asset_path, history_valid_svctag_path, logger)
		# Use valid service tags to call Dell API, and parse JSON data into a list of DellAsset entities
		api_entities_L = api_entities_batch(target_svc_L, api_url, logger)
		existing_entities_L = load_dell_asset(dell_asset_path, existing_svc_S)
		# Translate all Warranties of each DellAsset, and find those warranties without available translation
		if len(api_entities_L) > 0: 
			dell_asset_L, NA_dict = translate_dell_warranty(yml_url_path=transl_url, dell_asset_L=api_entities_L)
			# Save output into the csv_path
			save_object_to_path(object_L=dell_asset_L, output_path=csv_output_path)
			# Email the csv output and also all NA translation
			if email_job_output_translation(svctag=svctag, config=config, csv_path=csv_output_path, NA_dict=NA_dict):
				logger.append("Sending email done")
	except:
		send_email(subject=config['email_subject_error'], text=traceback.print_exc(), config=config)
		logger.append("Error when runing the job:")
		logger.append(traceback.print_exc())
	logger.append("\nFINISH>>>>>>>>>>>>>>>> main")
	save_object_to_path(object_L=logger, output_path=log_output_path)
	if logger.has_error:
		send_email(subject=config['email_subject_error'] % (current_time, svctag), text=logger.get_error_only(), config=config)
	if logger.has_warn:
		send_email(subject=config['email_subject_warning'] % (current_time, svctag), text=logger.get_warn_only(), config=config)
		
