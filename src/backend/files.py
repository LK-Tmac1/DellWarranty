# -*- coding: utf-8 -*-
from zipfile import ZipFile
from entity import DellAsset
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
            if resp.status_code == 200:
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

    def file_names(self):
        return self.file.namelist()

    def find_file_regex(self, regex):
        result_list = list([])
        for data in self.file_list:
            if re.match(regex, data.filename):
                result_list.append(data.filename)
        return result_list

    def add_new_file_batch(self, file_path_list):
        # duplicated files are allowed, so be careful
        for file_path in file_path_list:
            if FileUtility.is_path_existed(file_path):
                arcname = os.path.split(file_path)[1]
                self.file.write(filename=file_path, arcname=arcname)

    def get_member_content(self, file_name):
        try:
            return self.file.read(file_name)
        except KeyError:
            print 'ERROR: No %s in zip file' % file_name

