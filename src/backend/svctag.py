import itertools, requests, time

dell_support_url = "http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/"
api_offset = 50
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class ServiceTagGenerator(object):
    svc_set = set([])

    def __init__(self, svc_tag):
        pattern = list([])
        wildcard_indexes = list([])
        for i in xrange(len(svc_tag)):
            c = svc_tag[i]
            pattern.append(".")
            wildcard_indexes.append(i)
            if c.upper() in letters: # not a wildcard "."
                pattern[-1] = c.upper()
                wildcard_indexes.pop()
        total = len(wildcard_indexes)
        permutations = itertools.product(letters, repeat=total)
        for perm in permutations:
            for i in xrange(total):
                pattern[wildcard_indexes[i]] = perm[i]
                self.svc_set.add(''.join(pattern))

    def get_flatten_svc(self):
        # Given a list of service tags, return the concatenated string delimited by "|"
        flatten_list = list([])
        svc_list = self.svc_set
        total, turn = len(self.svc_set) / api_offset, 0
        while turn <= total:
            begin = turn * api_offset
            end = min(begin+api_offset, len(self.svc_set))
            flatten_list.append('|'.join(svc_list[begin:end]))
            turn += 1
        return flatten_list

    def filter_history(self, history_set):
        self.svc_set = self.svc_set - history_set

    def remove_invalid_batch(self):
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

    @staticmethod
    def check_svc_valid(svc_tag):
        response = requests.get(dell_support_url + svc_tag)
        if not response or response.status_code != 200:
            raise requests.exceptions.ConnectionError
        return str(response.url).endswith("False")
