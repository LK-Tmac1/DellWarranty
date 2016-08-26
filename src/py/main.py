from svctag_process import valid_svctags_batch
from api_json import get_entities_batch
from utility import read_file, get_current_time, parse_cmd_args, save_object_to_path
from translate import translate_dell_warranty
from email_job import send_email, email_job_output_translation
import traceback, sys
from constant import file_config_name

required_arg_list = ['--parent_path=', '--svctag=']

if __name__ == "__main__":
	# Prepare arguments for a job
	arguments = parse_cmd_args(sys.argv, required_arg_list)
	print arguments
	#"""
	svctags = arguments['svctag']
	parent_path = arguments['parent_path']
	config = read_file(parent_path + file_config_name, isYML=True)
	valid_svctag_path = parent_path + "valid_svctags.txt"
	csv_output_path = parent_path + "output/"
	url = config['dell_api_url'] % config["dell_api_key"]
	transl_url = config["translation_url"]
	current_time = get_current_time()
	config['email_subject_error'] = config['email_subject_error'] % (current_time, suffix, digit)
	config['email_subject_warning'] = config['email_subject_warning'] % (current_time, suffix, digit)	
	try:
		# Generate valid service tags from all possible random permutations
		valid_svctag_L = valid_svctags_batch(suffix=suffix, dell_support_url=config["dell_support_url"], d=digit, valid_svctag_path=valid_svctag_path)
		# print valid_svctag_L, "============ main"
		# Use valid service tags to call Dell API, and parse JSON data into a list of DellAsset entities
		dell_entities_L = get_entities_batch(svctag_L=valid_svctag_L, url=url, config=config)
		# Translate all Warranties of each DellAsset, and find those warranties without available translation
		if len(dell_entities_L) > 0: 
			dell_asset_L, NA_dict = translate_dell_warranty(yml_url_path=transl_url, dell_asset_L=dell_entities_L)
			# Save output into the csv_path
			save_object_to_path(object_L=dell_asset_L, output_path=csv_output_path)
			# Email the csv output and also all NA translation
			if email_job_output_translation(suffix=suffix, config=config, csv_path=csv_output_path, NA_dict=NA_dict):
				print "Sending email done..."
	except:
		send_email(subject=config['email_subject_error'], text=traceback.print_exc(), config=config)
	print "HERE>>>>>>>>>>>>>>>> main"
	#"""
