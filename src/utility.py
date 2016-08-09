import yaml, requests


def load_yaml_file(yml_path, isURL=False):
	# Read input file in .yml format, either the yml_path is a URL or or local path
	if isURL:
		resp = requests.get(yml_path)
		return yaml.load(resp.content)
	else:
		with open(yml_path, "r") as value:
			return yaml.load(value)

def save_entity_csv(dell_asset_L, output_path):
	with open(output_path, 'w') as output:
		for dell in dell_asset_L:
			output.write(str(dell) + "\n")

def send_email(subject, text, attachment_L, config):
	data = {"from": config["mail_from"],
			"to": config["mail_to"],
			"cc": config["mail_cc"],
			"subject": subject,
			"text": text}
	if data["to"] == data["cc"]:
		data.pop("cc")
	return requests.post(config["mail_post_url"], auth=("api", config["mail_api_key"]), data=data, files=attachment_L)
