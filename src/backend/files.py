# -*- coding: utf-8 -*-
from zipfile import ZipFile
import re, os, requests, yaml


class FileUtility(object):
    @staticmethod
    def is_path_existed(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def delete_file(file_path):
        if FileUtility.is_path_existed(file_path):
            os.remove(file_path)

    @staticmethod
    def read_file(file_path, isYML, isURL=False, lines=False):
        # Read input file in .yml format, either the yml_path is a URL or or local path
        result = None
        if isURL:
            resp = requests.get(file_path)
            if str(resp.status_code) == '200':
                result = yaml.load(resp.content) if isYML else resp.content
        else:
            if FileUtility.is_path_existed(file_path):
                with open(file_path, "r") as value:
                    result = yaml.load(value) if isYML else value.read()
        if lines and result:
            result = result.split("\n")
        return result

    @staticmethod
    def save_object_to_path(value, output_path, isYML=False):
        parent_dir = output_path[0:output_path.rfind("/")]
        # If output parent dir does not exist, create it
        if not FileUtility.is_path_existed(parent_dir):
            os.makedirs(parent_dir)
        with open(output_path, 'w') as output:
            if isYML:
                yaml.safe_dump(value, output)
            else:
                object_list = value
                if type(object_list) is not list:
                    object_list = [object_list]
                content = list([])
                for obj in object_list:
                    content.append(str(obj))
                    if content[-1][-1] != '\n':
                        content.append('\n')
                    output.write("".join(content))
        return True


class ZipFileSVC(object):
    def __init__(self, zip_file_path, mode='r'):
        self.file_path = zip_file_path
        self.file = ZipFile(file=zip_file_path, mode=mode)
        self.file_list = self.file.filelist
        self.invalid_svc = set([])
        self.history_svc = set([])

    def is_history(self, svc):
        return svc in self.history_svc

    def is_known(self, svc):
        return svc in self.invalid_svc or svc in self.history_svc

    def file_names(self):
        return self.file.namelist()

    def find_file_regex(self, regex):
        result_list = list([])
        for data in self.file_list:
            if re.match(regex, data.filename):
                result_list.append(data.filename)
        return result_list

    def add_new_file(self, file_path):
        # duplicated files are allowed
        if FileUtility.is_path_existed(file_path):
            arcname = os.path.split(file_path)[1]
            self.file.write(filename=file_path, arcname=arcname)

    def get_member_content(self, file_name):
        try:
            return self.file.read(file_name).decode('utf-8')
        except KeyError:
            print 'ERROR: No %s in zip file' % file_name


# path = "/Users/kunliu/dell/all.zip"
# zipfile = ZipFileSVC(path, mode='a')
# print zipfile.file_names(),'----'
#zipfile.add_new_file('/Users/kunliu/dell/valid_svctags.txt')
#print zipfile.get_member_content('valid_svctags.txt')
#print zipfile.file_names()
