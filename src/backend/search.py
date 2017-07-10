from constant import api_offset, letters, dell_support_url
import itertools, requests, time, urllib2


class ServiceTagGenerator(object):
    svc_set = svc_list = None
    unknown_index_list = list([])

    def __init__(self, pattern):
        self.pattern = pattern
        for i in xrange(len(self.pattern)):
            if self.pattern[i] not in letters:
                self.unknown_index_list.append(i)

    @staticmethod
    def check_letter_valid(letter):
        return letter and letter.upper() in letters

    @staticmethod
    def check_svc_valid(svc):
        response = requests.get(dell_support_url + svc).url
        if response.status_code == 403:
            pass
        return response and response.status_code == 200 and \
            str(response.url).endswith("False")

    def svc_tag_flatten(self):
        # Given a list of service tags, return the concatenated string delimited by "|"
        flatten_list = list([])
        total, turn = len(self.svc_list) / api_offset, 0
        while turn <= total:
            begin = turn * api_offset
            end = min(begin+api_offset, len(self.svc_list))
            temp_list = self.svc_list[begin:end]
            flatten_list.append('|'.join(temp_list))
            turn += 1
        return flatten_list

    def all_possible_svc(self):
        self.svc_list = list([])
        svc_list = list(self.pattern)
        permutations = itertools.product(letters, repeat=len(self.unknown_index_list))
        for perm in permutations:
            for i in xrange(len(self.unknown_index_list)):
                svc_list[self.unknown_index_list[i]] = perm[i]
                self.svc_list.append(''.join(svc_list))
        self.svc_set = set(self.svc_list)
        return self.svc_list

    def remove_history(self, history_set):
        self.svc_set = self.svc_set - history_set

    def remove_invalid(self):
        valid_svc = set([])
        max_retry = 5
        for svc in self.svc_set:
            try:
                for _ in xrange(max_retry):
                    if ServiceTagGenerator.check_svc_valid(svc):
                        valid_svc.add(svc)
            except requests.exceptions.ConnectionError:
                # sleep for 1 second to retry
                time.sleep(1)
        self.svc_set = valid_svc

svc = "FFFF4Z1"
print ServiceTagGenerator.check_svc_valid(svc=svc)
