from datetime import datetime
from utility import send_email, load_yaml_file


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

def email_csv_attachment(suffix, config, csv_path, NA_data=None):
	# If all services translation available, just send CSV as attachment
	# Otherwise, write the service_en and svctag as text on the email
	current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	subject = "CSV output generated on %s, %s" % (suffix, current_time)
	text = "No additional translation needed for this %s" % (suffix)
	if NA_data is not None:
		subject = "Translation request on %s, %s " % (suffix, current_time)
		text = yaml.safe_dump(NA_data, allow_unicode=True, default_flow_style=False)
	files = [("attachment", open(csv_path))]
	return send_email(subject=subject, text=text, files=files, config=config)

def update_NA_translation(csv_input_path, translate_url_path, csv_output_path):
	# Given a CSV file, update all the services translations based on the 
	# translate url path provided, and output another csv file
	return ""

def translate_dell_warranty(yml_url_path, dell_asset_L):
	tran_dict = load_yaml_file(yml_url_path, isURL=True)
	tran_dict = filter_NA_translation(tran_dict)
	NA_dict = {}
	for dell_asset in dell_asset_L:
		for warranty in dell_asset.get_warranty():
			if warranty.service_en in tran_dict:
				warranty.service_ch = tran_dict[warranty.service_en]
			else:
				NA_dict[warranty.service_en] = dell_asset.svctag
	return dell_asset_L, NA_dict



