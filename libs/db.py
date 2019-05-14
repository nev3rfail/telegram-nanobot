import sqlite3
class Database:
    def __init__(self, dbpath, autocommit=True):
        self.dbconnection = sqlite3.connect(dbpath, check_same_thread=False)
        self.dbconnection.row_factory = sqlite3.Row

    def query(self, * args, ** kwargs):
        get_id = None
        if "get_id" in kwargs:
            get_id = True
            del kwargs['get_id']

        #https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.execute
        if len(args) == 2:
            cursor = self.dbconnection.execute(args[0], args[1])
        else:
            cursor = self.dbconnection.execute(args[0])

        if get_id and cursor.lastrowid:
            if autocommit:
                self.commit()
            return cursor.lastrowid
        elif cursor.rowcount != -1:
            if autocommit:
                self.commit()
            return cursor.rowcount
        else:
            return cursor.fetchall()


    def commit(self):
        return self.dbconnection.commit()
