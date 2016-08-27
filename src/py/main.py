from svctag_process import valid_svctags_batch
from api_json import get_entities_batch
from utility import read_file, get_current_time, parse_cmd_args, save_object_to_path
from translate import translate_dell_warranty
from email_job import send_email, email_job_output_translation
import traceback, sys
from constant import file_config_name, svc_delimitor

required_arg_list = ['--parent_path=', '--svctag=']

if __name__ == "__main__":
	# Prepare arguments for a job
	arguments = parse_cmd_args(sys.argv, required_arg_list)
	#"""
	parent_path = arguments['parent_path']
	svctags = arguments['svctag']
	svc_L = svctags.split(svc_delimitor)
	config = read_file(parent_path+"dell_config.yml", isYML=True, isURL=False)
	history_valid_svctag_path = parent_path + "valid_svctags.txt"
	dell_asset_path = parent_path + "dell_asset/"
	csv_output_path = parent_path + "output/"
	api_url = config['dell_api_url'] % config["dell_api_key"]
	transl_url = config["translation_url"]
	current_time = get_current_time()
	config['email_subject_error'] = config['email_subject_error'] % (current_time, svc_L)
	config['email_subject_warning'] = config['email_subject_warning'] % (current_time, svc_L)
	log_output_path = "%s%s_svctag=%s.txt" % (parent_path, current_time, svc_L)
	log_Q = []
	try:
		target_svctag_L = target_svctags_batch(svc_L=svc_L, dell_support_url=config["dell_support_url"],dell_asset_path=dell_asset_path, history_valid_svctag_path=history_valid_svctag_path, logging=log_Q)
		# Use valid service tags to call Dell API, and parse JSON data into a list of DellAsset entities
		dell_entities_L = get_entities_batch(svctag_L=target_svctag_L, url=api_url, config=config, logging=log_Q, dell_asset_path=dell_asset_path)
		# Translate all Warranties of each DellAsset, and find those warranties without available translation
		if len(dell_entities_L) > 0: 
			dell_asset_L, NA_dict = translate_dell_warranty(yml_url_path=transl_url, dell_asset_L=dell_entities_L)
			# Save output into the csv_path
			save_object_to_path(object_L=dell_asset_L, output_path=csv_output_path)
			# Email the csv output and also all NA translation
			if email_job_output_translation(suffix=suffix, config=config, csv_path=csv_output_path, NA_dict=NA_dict):
				log_Q.append("Sending email done")
	except:
		send_email(subject=config['email_subject_error'], text=traceback.print_exc(), config=config)
		log_Q.append("Error when runing the job:")
		log_Q.append(traceback.print_exc())
	log_Q.append("\nFINISH>>>>>>>>>>>>>>>> main")
	save_object_to_path(object_L=log_Q, output_path=log_output_path)
