import requests
from utility import is_path_existed


class Email(object):
    def __init__(self, **kwargs):
        self.data = {"from": kwargs["mail_from"], "to": kwargs["mail_to"], "cc": kwargs["mail_cc"]}
        self.texts = list([])
        self.subject = ""
        self.attachments_list = list([])

    def add_text(self, text):
        self.texts.append(text)

    def add_subject(self, subject):
        self.subject = subject

    def add_attachment(self, file_path):
        if is_path_existed(file_path):
            self.attachments_list.append(("attachment", open(file_path)))

    def send(self, subject, cc_mode=False, **kwargs):
        data = self.data.copy()
        data["subject"] = subject
        data["text"] = "\n".join(self.texts)
        if not cc_mode:
            data.pop('cc')
        result = requests.post(kwargs["mail_post_url"], auth=("api", kwargs["mail_api_key"]), data=data,
                               files=self.attachments_list)
        return result.status_code == 200
