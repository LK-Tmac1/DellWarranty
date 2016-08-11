from svctag_process import valid_svctags_batch
from api_json import get_entities_batch
from utility import load_yaml_config, get_current_time, send_email
from translate import translate_dell_warranty
import traceback

required_arg_list = ['--config_path=', '--suffix=', '--digit=']

if __name__ == "__main__":
	print sys.argv
	# Prepare arguments for a job
	arguments = parse_cmd_args(sys.argv, config)
	suffix = arguments['suffix']
	digit = arguments['digit']
	config = load_yaml_config(arguments['config_path'])
	csv_output_path = "/output/%s_%s" % (suffix, get_current_time().replace(" ", "_"))
	url = config['dell_api_url'] % config["dell_api_key"]
	transl_url = config["git_translate_url"]
	try:
		# Generate valid service tags from all possible random permutations
		valid_svctag_L = valid_svctags_batch(suffix=suffix, dell_support_url=config["dell_support_url"], d=digit)
		# Use valid service tags to call Dell API, and parse JSON data into a list of DellAsset entities
		dell_entities_L = get_entities_batch(svctag_L=valid_svctag_L, url=url)
		# Translate all Warranties of each DellAsset, and find those warranties without available translation
		dell_asset_L, NA_dict = translate_dell_warranty(yml_url_path=transl_url, dell_asset_L=dell_entities_L)
		# Save output into the csv_path
		save_entity_csv(dell_asset_L=dell_asset_L, output_path=csv_output_path)
		# Email the csv output and also all NA translation
		email_csv_attachment(suffix=suffix, config=config, csv_path=csv_output_path, NA_dict=NA_dict)
	except Exception:
		subject = "Job running error on %s, suffix=%s, digit=%s" % (get_current_time(), suffix, digit)
		send_email(subject=subject, text=traceback.print_exc(), attachment_L=None, config=config)

