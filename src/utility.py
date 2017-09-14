# -*- coding: utf-8 -*-

import yaml, datetime, time, os, requests
from dateutil.parser import parse


class FileUtil(object):
    @staticmethod
    def is_path_existed(file_path):
        return file_path and os.path.exists(file_path.strip())

    @staticmethod
    def delete_file(file_path):
        if FileUtil.is_path_existed(file_path):
            try:
                os.remove(file_path)
            except Exception:
                return

    @staticmethod
    def read_file(file_path, isYML, isURL=False, lines=False):
        # Read input file in .yml format, either the yml_path is a URL or or local path
        result = None
        if isURL:
            resp = requests.get(file_path)
            if resp.status_code == 200:
                result = yaml.load(resp.content) if isYML else resp.content
        else:
            if FileUtil.is_path_existed(file_path):
                with open(file_path, "r") as value:
                    result = yaml.load(value) if isYML else value.read()
        if lines and result:
            result = result.split("\n")
        return result

    @staticmethod
    def save_object_to_path(object_list, output_path, isYML=False, append=False):
        if not object_list:
            return
        if type(object_list) is not list:
            object_list = [object_list]
        content = list([])
        for obj in object_list:
            content.append(str(obj))
        if content[-1] != "":
            content.append("")  # last line always empty
        content = "\n".join(content)

        parent_dir = output_path[0:output_path.rfind(os.sep)]
        # If output parent dir does not exist, create it
        if not FileUtil.is_path_existed(parent_dir):
            os.makedirs(parent_dir)
        output = open(output_path, mode="a" if append else "w")
        try:
            if isYML:
                yaml.safe_dump(object_list, output)
            else:
                output.write(content)
        finally:
            output.close()

datetime_str_format = '%Y-%m-%d %H:%M:%S'
date_str_format = "%s年%s月%s日"
time_str_format = "%H:%M:%S"
date_str_format_search = "%Y-%m-%d"
hour_str_format = "%H小时%M分钟%S秒"


class DateTimeUtil(object):
    @staticmethod
    def parse_str_date(str_date):
        if not str_date:
            return ""
        try:
            date_object = parse(str_date)
            return date_str_format % (date_object.year, date_object.month, date_object.day)
        except Exception:
            return str_date

    @staticmethod
    def get_current_datetime(is_format=True, is_date=False, str_format=datetime_str_format):
        now = datetime.datetime.now()
        if is_format:
            if is_date:
                now = now.strftime(date_str_format_search)
            else:
                now = now.strftime(str_format)
        return now

    @staticmethod
    def datetime_diff(time1, time2):
        t1 = datetime.datetime.strptime(time1, datetime_str_format)
        t2 = datetime.datetime.strptime(time2, datetime_str_format)
        diff = max(t1, t2) - min(t1, t2)
        return time.strftime(hour_str_format, time.gmtime(diff.seconds))


class Logger(object):
    def __init__(self, name, verbose):
        self.messages = list([])
        if name:
            self.messages.append(name)
        self.has_error = False
        self.verbose = verbose

    def add_message(self, message, header=""):
        current_time = DateTimeUtil.get_current_datetime(str_format=time_str_format)
        self.messages.append("%s %s %s" % (current_time, header, message))
        if self.verbose:
            print self.messages[-1]

    def info(self, message):
        self.add_message(message, "")

    def warn(self, message):
        self.add_message(message, " 提示：")

    def error(self, message):
        self.has_error = True
        self.add_message(message, " 错误：")

    def save(self, output_path):
        FileUtil.save_object_to_path(self.__repr__(), output_path)

    def __repr__(self):
        return "\n".join(self.messages)

email_post_url = "https://api.mailgun.net/v3/sandbox37699e306f69436d8f89f81915ad9f0a.mailgun.org/messages"
email_from = "戴尔保修查询 <postmaster@sandbox37699e306f69436d8f89f81915ad9f0a.mailgun.org>"
email_to = "Hotmail <daierchaxun@hotmail.com>"
email_cc = "Kun <liukun1016@gmail.com>"


class Email(object):
    def __init__(self, email_api_key, **kwargs):
        self._from = kwargs.get("email_from", email_from)
        self._cc = kwargs.get("email_cc", email_cc)
        self._to = kwargs.get("email_to", email_to)
        self._post_url = kwargs.get("email_post_url", email_post_url)
        self._api_key = email_api_key
        self.subject = kwargs.get("subject", "邮件")
        self.text_list = list([])
        self.attachment_list = list([])

    def update_subject(self, subject):
        self.subject = subject

    def add_text(self, text, append=True):
        if append:
            self.text_list.append(text)
        else:
            self.text_list = list([text])

    def add_attachment(self, file_path):
        self.attachment_list.append(("attachment", open(file_path)))

    def send(self, cc_mode=True):
        data = {"from": self._from, "to": self._to,
                "subject": self.subject, "text": "\n".join(self.text_list)
                }
        if cc_mode:
            data["cc"] = self._cc
        auth = ("api", self._api_key)
        result = requests.post(self._post_url, auth=auth, data=data,files=self.attachment_list)
        return result.status_code == 200
