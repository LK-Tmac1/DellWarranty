import yaml, requests, datetime

def parse_cmd_args(arguments, required_arg_list):
	arg_map = {}
	for iarg in range(1,len(arguments)):
		arg = arguments[iarg]
		for a in required_arg_list:
			if arg.startswith(a):
				arg_map[a[2:-1]] = arg.split("=",1)[1]
				break
	return arg_map


def get_current_time():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def load_yaml_file(yml_path, isURL=False):
	# Read input file in .yml format, either the yml_path is a URL or or local path
	if isURL:
		resp = requests.get(yml_path)
		return yaml.load(resp.content)
	else:
		with open(yml_path, "r") as value:
			return yaml.load(value)

def verify_job_parameter(config_path, password, suffix, digit):
	config = load_yaml_file(config_path)
	if password != config['password']:
		return 1
	if len(suffix) + int(digit) != 7:
		return 2
	else:
		return 0

def save_entity_csv(dell_asset_L, output_path):
	with open(output_path, 'w') as output:
		for dell in dell_asset_L:
			output.write(str(dell) + "\n")
	return True

def send_email(subject, text, attachment_L, config):
	data = {"from": config["mail_from"],
			"to": config["mail_to"],
			"cc": config["mail_cc"],
			"subject": subject,
			"text": text}
	if data["to"] == data["cc"]:
		data.pop("cc")
	result = requests.post(config["mail_post_url"], auth=("api", config["mail_api_key"]), data=data, files=attachment_L)
	return result.status_code == 200

def email_csv_attachment(suffix, config, csv_path, NA_dict):
	# If all services translation available, just send CSV as attachment
	# Otherwise, write the service_en and svctag as text on the email
	current_time = get_current_time()
	subject = "CSV output generated on %s, %s" % (suffix, current_time)
	text = "No additional translation needed for this %s" % (suffix)
	if NA_dict is not None:
		subject = "Translation request on %s, %s " % (suffix, current_time)
		text = yaml.safe_dump(NA_dict, allow_unicode=True, default_flow_style=False)
	files = [("attachment", open(csv_path))]
	return send_email(subject=subject, text=text, files=files, config=config)
