# -*- coding: utf-8 -*-

import itertools, requests, time
from utility import FileUtil

dell_support_url = "http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/"
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class SVCGenerator(object):
    target_svc_set = set([])
    existed_svc_set = set([])
    invalid_history_count = 0

    def __init__(self, svc_tag, logger):
        self.logger = logger
        # Initialize target svc set by regex and permutations
        pattern = list([])
        wildcard_indexes = list([])
        for i in xrange(len(svc_tag)):
            c = svc_tag[i]
            pattern.append(".")
            wildcard_indexes.append(i)
            if c.upper() in letters: # not a wildcard "."
                pattern[-1] = c.upper()
                wildcard_indexes.pop()
        self.regex = "".join(pattern)
        total = len(wildcard_indexes)
        permutations = itertools.product(letters, repeat=total)
        for perm in permutations:
            for i in xrange(total):
                pattern[wildcard_indexes[i]] = perm[i]
                self.target_svc_set.add(''.join(pattern))

    def get_file_name(self):
        return self.regex.replace(".", "?")

    def target_svc_size(self):
        return len(self.target_svc_set)

    def split_existed(self, existed_svc):
        # Split existed svc from target
        for svc in existed_svc:
            if svc in self.target_svc_set:
                self.existed_svc_set.add(svc)
                self.target_svc_set.remove(svc)
        self.logger.info("已经存在的查询码历史：%s" % len(self.existed_svc_set))

    def filter_invalid_history(self, invalid_history_file_path):
        # If invalid history provided, remove those invalid from target svc set
        if FileUtil.is_path_existed(invalid_history_file_path):
            with open(invalid_history_file_path, mode='r') as invalid_history_file:
                # read the history file line by line, in case file too large
                for svc in invalid_history_file:
                    svc = svc.replace("\n", "")
                    if len(svc) == 7 and svc in self.target_svc_set:
                        self.invalid_history_count += 1
                        self.target_svc_set.remove(svc)
                    if not self.target_svc_set:
                        break
        self.logger.info("已知的本地非法查询码历史：%s" % self.invalid_history_count)

    def find_new_invalid_svc(self, invalid_history_file_path):
        # Use dell support URL to check those unknown even after invalid history
        valid_set = set([])
        max_retry = 3 # retry 3 times at most
        new_invalid_count = 0
        for svc in self.target_svc_set:
            for i in xrange(max_retry):
                try:
                    if i == max_retry - 1:
                        time.sleep(1) # last time retry, sleep for 1 second
                    if SVCGenerator.check_svc_valid(svc):
                        valid_set.add(svc)
                    else:
                        new_invalid_count += 1
                        self.logger.info("不合法：%s " % svc)
                        # Append new invalid SVC into history file if provided
                        FileUtil.save_object_to_path(svc, invalid_history_file_path, append=True)
                    break
                except requests.exceptions.ConnectionError:
                    # if ConnectionError, pass
                    continue
            else:
                self.logger.warn("检查查询码超时%s，忽略" % svc)
        self.target_svc_set = valid_set
        self.logger.info("新增%s个不合法的查询码" % new_invalid_count)

    def generate_target_svc_batch(self, existed_svc, invalid_history_file_path):
        self.split_existed(existed_svc)
        self.filter_invalid_history(invalid_history_file_path)
        self.find_new_invalid_svc(invalid_history_file_path)

    def __repr__(self):
        return "SVC=%s\tTarget=%s\tExisted=%s" % (self.regex, len(self.target_svc_set), len(self.existed_svc_set))

    @staticmethod
    def check_svc_valid(svc_tag):
        response = requests.get(dell_support_url + svc_tag)
        if not response or response.status_code != 200:
            raise requests.exceptions.ConnectionError
        return not str(response.url).endswith("False")
