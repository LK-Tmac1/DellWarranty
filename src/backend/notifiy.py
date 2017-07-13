# -*- coding: utf-8 -*-
import requests
from utility import is_path_existed

mail_post_url = "https://api.mailgun.net/v3/sandbox37699e306f69436d8f89f81915ad9f0a.mailgun.org/messages"
mail_from = "戴尔保修查询 <postmaster@sandbox37699e306f69436d8f89f81915ad9f0a.mailgun.org>"
mail_to = "Hotmail <daierchaxun@hotmail.com>"
mail_cc = "Kun <liukun1016@gmail.com>"


class Email(object):
    def __init__(self, mail_api_key, **kwargs):
        self._from = kwargs.get("mail_from", mail_from)
        self._cc = kwargs.get("mail_cc", mail_cc)
        self._to = kwargs.get("mail_to", mail_to)
        self._post_url = kwargs.get("mail_post_url", mail_post_url)
        self._api_key = mail_api_key
        self.subject = ""
        self.text_list = list([])
        self.attachment_list = list([])

    def update_subject(self, subject):
        self.subject = subject

    def add_text(self, text, append=True):
        if append:
            self.text_list.append(text)
        else:
            self.text_list = list([text])

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
        data = {"from": self._from, "to": self._to,
                "subject": self.subject, "text": "\n".join(self.text_list)}
        if cc_mode:
            data["cc"] = self._cc
        auth = ("api", self._api_key)
        result = requests.post(self._post_url, auth=auth, data=data,files=self.attachment_list)
        return result.status_code == 200
