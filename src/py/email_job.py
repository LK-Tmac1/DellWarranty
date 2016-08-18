import requests, yaml
from utility import get_current_time
from translate import reverse_NA_translation


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
	subject_prefix = "[Job done] "
	text = "No additional translation needed for this %s" % (suffix)
	if NA_dict is not None:
		subject_prefix = "[Need Translation] "
		text = "Translation request on %s, %s\n\n\n" % (suffix, current_time)
		NA_dict = reverse_NA_translation(NA_dict)
		for k, v in NA_dict.items():
			temp = str(k) + ": " + str(v)
			text += yaml.safe_dump(temp, allow_unicode=True, default_flow_style=False)
	files = [("attachment", open(csv_path))]
	return send_email(subject=subject_prefix + subject, text=text, attachment_L=files, config=config)
