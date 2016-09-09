# -*- coding: utf-8 -*-

import requests, yaml, sys
from utility import get_current_time, diff_two_time
from translate import reverse_NA_translation

reload(sys)
sys.setdefaultencoding('utf8')


def send_email(subject, text, config, attachment_L=None, cc_mode=True):
	data = {"from": config["mail_from"],
			"to": config["mail_to"],
			"cc": config["mail_cc"],
			"subject": subject,
			"text": text}
	if not cc_mode:
		data.pop('cc')
	result = requests.post(config["mail_post_url"], auth=("api", config["mail_api_key"]), data=data, files=attachment_L)
	return result.status_code == 200


def email_job_output_translation(svctag, config, csv_path, NA_dict, additional_text=""):
	# If all services translation available, just send CSV as attachment
	# Otherwise, write the service_en and svctag as text on the email
	end_time = get_current_time()
	subject = "%s %s %s" % ('查询结果成功', end_time, svctag)
	text = "全部已翻译."
	if bool(NA_dict):
		subject = "[需要翻译] %s" % subject
		text = "需要翻译的机器保修服务标签:\n"
		NA_dict = reverse_NA_translation(NA_dict)
		for k, v in NA_dict.items():
			temp = str(k) + ": " + str(v)
			text += yaml.safe_dump(temp, allow_unicode=True, default_flow_style=False)
	files = [("attachment", open(csv_path))] if csv_path is not None else None
	text = "%s\n%s" % (text, additional_text)
	return send_email(subject=subject, text=text, attachment_L=files, config=config)
