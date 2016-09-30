import requests
from utility import is_path_existed

def send_email(subject, text, config, attachment_path_L=None, cc_mode=False, additional_text=""):
	data = {"from": config["mail_from"],
			"to": config["mail_to"],
			"cc": config["mail_cc"],
			"subject": subject,
			"text": text + "\n" + additional_text}
	if not cc_mode:
		data.pop('cc')
	attachment_L = []
	if attachment_path_L is not None and len(attachment_path_L) > 0:
		for path in attachment_path_L:
			if is_path_existed(path):
				attachment_L.append(("attachment", open(path)))
	result = requests.post(config["mail_post_url"], auth=("api", config["mail_api_key"]), data=data, files=attachment_L)
	return result.status_code == 200