from svctag_process import valid_svctags_batch
from api_json import get_entities_batch
from utility import read_file, get_current_time, parse_cmd_args, save_object_to_path
from translate import translate_dell_warranty
from email_job import send_email, email_csv_attachment
import traceback, sys, os

# python main.py --config_path=/Users/kunliu/Desktop/work/dell_config.yml --suffix=3VG2W1 --digit=1

required_arg_list = ['--config_path=', '--suffix=', '--digit=']
global_parent_path = "/Users/kunliu/Desktop/dell_warranty/"

if __name__ == "__main__":
	print "Starting..."
	# Prepare arguments for a job
	arguments = parse_cmd_args(sys.argv, required_arg_list)
	suffix = arguments['suffix']
	digit = arguments['digit']
	config = read_file(arguments['config_path'], isYML=True)
	valid_svctag_path = "%s/valid_svctags/suffix=%s_d=%s.txt" % (global_parent_path, suffix, digit)
	csv_output_path = "%s/output/%s/%s.csv" % (global_parent_path, suffix, get_current_time().replace(" ", "_"))
	url = config['dell_api_url'] % config["dell_api_key"]
	transl_url = config["git_translate_url"]
	error_subject = "[Error] Job running on %s, suffix=%s, digit=%s" % (get_current_time(), suffix, digit)
	
	try:
		# Generate valid service tags from all possible random permutations
		valid_svctag_L = valid_svctags_batch(suffix=suffix, dell_support_url=config["dell_support_url"], d=digit, valid_svctag_path=valid_svctag_path)
		# Use valid service tags to call Dell API, and parse JSON data into a list of DellAsset entities
		dell_entities_L = get_entities_batch(svctag_L=valid_svctag_L, url=url)
		# Translate all Warranties of each DellAsset, and find those warranties without available translation
		dell_asset_L, NA_dict = translate_dell_warranty(yml_url_path=transl_url, dell_asset_L=dell_entities_L)
		# Save output into the csv_path
		save_object_to_path(object_L=dell_asset_L, output_path=csv_output_path)
		# Email the csv output and also all NA translation
		email_csv_attachment(suffix=suffix, config=config, csv_path=csv_output_path, NA_dict=NA_dict)
	except ValueError:
		print "HERE>>>>>>>>>>>>>>>>"
		text = "Service Profile Throttle Limit Reached\nURL=" + url
		send_email(subject=error_subject, text=text, attachment_L=None, config=config)
	except:
		send_email(subject=error_subject, text=traceback.print_exc(), attachment_L=None, config=config)

