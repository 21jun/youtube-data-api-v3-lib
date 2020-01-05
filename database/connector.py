import pymysql


class DataBase:

    def __init__(self):
        self.host = "localhost"
        self.port = 3306
        self.db = "yt" # your mysql schema name
        self.user = "root"
        self.password = "1qazxc"
        self.autocommit = True
        self.charset = "utf8mb4"

        self.con = None
        self.cur = None

        self.__connect__()

    def __connect__(self):
        if (self.con is not None) or (self.cur is not None):
            return

        self.con = pymysql.connect(host=self.host, port=self.port, db=self.db,
                                   user=self.user, password=self.password,
                                   charset=self.charset, autocommit=self.autocommit)
        self.cur = self.con.cursor()
        print("connection complete")

    def __disconnect__(self):
        self.con.close()
        self.cur = None
        self.con = None

    def execute(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        self.__disconnect__()
