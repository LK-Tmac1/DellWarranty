import MySQLdb


class MySQLClient(object):

    def __init__(self, **kwargs):
        self.db_name = "dellwarranty"
        if False:
            self.client = MySQLdb.connect(host="localhost", user="root", passwd="password", db="dellwarranty")
            self.cursor = self.client.cursor()

    def execute_query(self, query, result=True):
        result_list = []
        self.cursor().execute(query)
        self.cursor.commit()
        if result:
            for i in xrange(self.cursor.rowcount):
                result_list.append(self.cursor.fetchone())
        return result_list if result else None

    @staticmethod
    def build_filters(stmt_list, filters):
        if not filters: return
        stmt_list.append("WHERE")
        for filter in filters:
            stmt_list.append(filter)
            stmt_list.append(",")
        if stmt_list[-1] == ",":
            stmt_list.pop()

    @staticmethod
    def build_select_statement(db_name, tb_name, target_columns=None, filters=None):
        select_statement = list(["SELECT"])
        if not target_columns:
            select_statement.append("*")
        else:
            for target in target_columns:
                select_statement.append("`%s`" % target)
                select_statement.append(",")
            if select_statement[-1] == ',':
                select_statement.pop()
        select_statement.append("FROM %s.%s" % (db_name, tb_name))
        MySQLClient.build_filters(select_statement, filters)
        return " ".join(select_statement)

    @staticmethod
    def build_delete_statement(db_name, tb_name, filters=None):
        delete_statement = list(["DELETE * "])
        delete_statement.append("FROM %s.%s" % (db_name, tb_name))
        MySQLClient.build_filters(delete_statement, filters)
        return " ".join(delete_statement)

    @staticmethod
    def build_insert_statement(db_name, tb_name, columns, value_string):
        insert_statement = list(["INSERT INTO %s.%s" % (db_name, tb_name)])
        insert_statement.append("(")
        for col in columns:
            insert_statement.append(col)
        insert_statement.append(") VALUES")
        insert_statement.append(value_string)
        return " ".join(insert_statement)


class InvalidHistoryClient(MySQLClient):

    def __init__(self, **kwargs):
        self.tb_name = "InvalidHistory"
        self.svc_column = "svc_tag"
        MySQLClient.__init__(self, **kwargs)

    def get_invalid_from_regex(self, svc_tag):
        filters = ["AND %s REGEXP '%s'" % (self.svc_column, svc_tag)]
        sql_stmt = self.build_select_statement(self.db_name, self.tb_name, self.svc_column, filters)
        return self.execute_query(sql_stmt, result=True)

    def delete_invalid_batch(self, svc_list):
        filters = self.svc_column
        filters += " IN (%s)" % ', '.join("'{0}'".format(svc) for svc in svc_list)
        sql_stmt = MySQLClient.build_delete_statement(self.db_name, self.tb_name, filters)
        self.execute_query(sql_stmt, result=False)

    def insert_invalid_batch(self, svc_list):
        value_string = ', '.join("('{0}')".format(svc) for svc in svc_list)
        sql_stmt = MySQLClient.build_insert_statement(self.db_name, self.tb_name, self.svc_column, value_string)
        self.execute_query(sql_stmt, result=False)
