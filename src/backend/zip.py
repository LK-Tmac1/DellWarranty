# -*- coding: utf-8 -*-
from zipfile import ZipFile
from utility import FileUtil
import re, os


class ZipFileSVC(object):
    def __init__(self, zip_file_path, mode='w'):
        self.file_path = zip_file_path
        self.file = ZipFile(file=zip_file_path, mode=mode)
        self.file_list = self.file.filelist

    def file_names(self):
        return self.file.namelist()

    def find_file_regex(self, regex):
        result_list = list([])
        for f in self.file_list:
            if len(f.filename) < 7:
                continue
            if re.match(regex, f.filename):
                file_name = f.filename.split(".")[0]
                result_list.append(file_name)
        return result_list

    def add_new_file_batch(self, file_path_list):
        # duplicated files are allowed, so be careful
        for file_path in file_path_list:
            if FileUtil.is_path_existed(file_path):
                self.file.write(filename=file_path, arcname=os.path.split(file_path)[-1])

    def get_member_content(self, file_name):
        try:
            return self.file.read(file_name)
        except KeyError:
            return None
