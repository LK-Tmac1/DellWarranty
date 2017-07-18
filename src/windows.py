# -*- coding: utf-8 -*-


class WindowsUtil(object):
    @staticmethod
    def convert_win_path(file_path):
        try:
            return unicode(file_path,'utf8') if file_path else None
        except TypeError:
            return file_path


class UnicodeStreamFilter:
    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding

    def write(self, s):
        if type(s) == str:
            s = s.decode("utf-8")
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)
