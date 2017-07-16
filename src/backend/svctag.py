import itertools, requests, time

dell_support_url = "http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/"
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class SVCTagContainer(object):
    target_svc_set = set([])
    existed_svc_set = set([])

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
        self.regex = "".join(pattern)
        self.output_name = self.regex.replace(".", "_")
        total = len(wildcard_indexes)
        permutations = itertools.product(letters, repeat=total)
        for perm in permutations:
            for i in xrange(total):
                pattern[wildcard_indexes[i]] = perm[i]
                self.target_svc_set.add(''.join(pattern))

    def get_output_name(self):
        return self.output_name

    def filter_history(self, history_set):
        if not history_set:
            return
        for svc in history_set:
            if svc in self.target_svc_set:
                self.target_svc_set.remove(svc)

    def split_existed(self, existed_svc):
        if existed_svc:
            for svc in existed_svc:
                if svc in self.target_svc_set:
                    self.existed_svc_set.add(svc)
                    self.target_svc_set.remove(svc)

    def remove_invalid_batch(self):
        # Given api SVC set, remove and return those invalid in a list
        valid_set = set([])
        invalid_list = list([])
        max_retry = 3
        for svc in self.target_svc_set:
            for _ in xrange(max_retry):
                try:
                    if SVCTagContainer.check_svc_valid(svc):
                        valid_set.add(svc)
                    else:
                        invalid_list.append(svc)
                    break
                except requests.exceptions.ConnectionError:
                    # sleep for 1 second to retry
                    time.sleep(1)
        self.target_svc_set = valid_set
        return invalid_list

    def svc_size(self):
        return len(self.target_svc_set)

    def __repr__(self):
        return "SVC=%s\tTarget=%s\tExisted=%s" % (self.regex, len(self.target_svc_set), len(self.existed_svc_set))

    @staticmethod
    def check_svc_valid(svc_tag):
        invalid_svc_list= ['ABCDEFP', 'ABCDEFQ', 'ABCDEFR', 'ABCDEFS', 'ABCDEFT', 'ABCDEFU', 'ABCDEFV', 'ABCDEFW', 'ABCDEFX',
                   'ABCDEFY', 'ABCDEFA', 'ABCDEFB', 'ABCDEFC', 'ABCDEFD', 'ABCDEFE', 'ABCDEFH', 'ABCDEFI', 'ABCDEFJ',
                   'ABCDEFK', 'ABCDEFL', 'ABCDEFM', 'ABCDEFN', 'ABCDEFO', 'ABCDEF0', 'ABCDEF5', 'ABCDEF6', 'ABCDEF8',
                   'ABCDEF9']
        invalid_svc_set = set(invalid_svc_list)
        return svc_tag not in invalid_svc_set

        """
        response = requests.get(dell_support_url + svc_tag)
        if not response or response.status_code != 200:
            raise requests.exceptions.ConnectionError
        return not str(response.url).endswith("False")
        """
