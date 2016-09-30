import requests, yaml, sys
from utility import get_current_time, diff_two_time, is_path_existed
from translate import reverse_NA_translation
from constant import email_job_finish_subject_prefix


def send_email(subject, text, config, attachment_path_L=None, cc_mode=False, additional_text=""):
	data = {"from": config["mail_from"],
			"to": config["mail_to"],
			"cc": config["mail_cc"],
			"subject": subject,
			"text": text + "\n" + additional_text}
	if not cc_mode:
		data.pop('cc')
	attachment_L = []
	for path in attachment_path_L:
		if is_path_existed(path):
			attachment_L.append(("attachment", open(path)))
	result = requests.post(config["mail_post_url"], auth=("api", config["mail_api_key"]), data=data, files=attachment_L)
	return result.status_code == 200