import MySQLdb


class DBClient(object):

    def __init__(self, **kwargs):
        self.db_name = kwargs["db_name"]
        if False:
            self.client = MySQLdb.connect(host=kwargs["host"], user=kwargs["user"],
                                      passwd=kwargs["passwd"], db=kwargs["db_name"])
            self.cursor = self.client.cursor()

    def execute_query(self, query):
        result_list = []
        try:
            self.cursor().execute(query)
            self.cursor.commit()
            for i in xrange(self.cursor.rowcount):
                result_list.append(self.cursor.fetchone())
        except:
            print "=======Exception for", query
        return result_list

    def build_select_statement(self, tb_name, target_columns=None, filter_map=None):
        select_statement = list(["SELECT"])
        if not target_columns:
            select_statement.append("*")
        else:
            for target in target_columns:
                select_statement.append("`%s`" % target)
                select_statement.append(",")
            select_statement.pop()
        select_statement.append("FROM %s.%s WHERE 1=1" % (self.db_name, tb_name))
        if filter_map:
            select_statement.append("AND")
            for k, v in filter_map.items():
                select_statement.append("`%s`=%s" % (k, v))
        return " ".join(select_statement)


class DellAssetClient(DBClient):

    def __init__(self):
        pass

class WarrantyClient(DBClient):

    def __init__(self):
        pass

class DellWarrantyClient(DBClient):
    def __init__(self):
        pass


class Solution(object):
    def convert(self, s, rowNum):
        if rowNum<=1: return 2
        temp = []
        for i in xrange(rowNum):
            temp.append([])
        row = 0; is_down = True
        for i in xrange(len(s)):
            # add s[i] to correct row
            temp[row].append(s[i])
            if is_down:
                row += 1
                if row == rowNum:
                    is_down = False
                    row -= 2
            else:
                if row == 0:
                    is_down = True
                    row += 1
                else:
                    row -= 1
        res_list = []
        for t in temp:
            res_list.append("".join(t))
        return "".join(res_list)

s="ABCDEF"; r = 3
print Solution().convert(s, r)