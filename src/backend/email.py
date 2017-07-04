import requests
from utility import is_path_existed


class Email(object):
    def __init__(self, **kwargs):
        self._from = kwargs["mail_from"]
        self._cc = kwargs["mail_cc"]
        self._to = kwargs["mail_to"]
        self._post_url = kwargs["mail_post_url"]
        self._api_key = kwargs["mail_api_key"]
        self.subject = ""
        self.text = ""
        self.attachment_list = list([])

    def update_subject(self, subject):
        self.subject = subject

    def update_text(self, text, append=True):
        self.text = self.text + text if append else text

    def add_attachment(self, file_path, append=True):
        if append:
            self.attachment_list.append(file_path)
        else:
            self.attachment_list = list([file_path])

    def add_multiple_attachments(self, attachment_list):
        for file_path in attachment_list:
            if is_path_existed(file_path):
                self.add_attachment(file_path)

    def send(self, cc_mode=False):
        data = {"from": self._from, "to": self._to, "subject": self.subject, "text": self.text}
        if cc_mode:
            data["cc"] = self._cc
        auth = ("api", self._api_key)
        result = requests.post(self._post_url, auth=auth, data=data,files=self.attachment_list)
        return result.status_code == 200
