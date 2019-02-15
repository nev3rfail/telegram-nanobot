
class DB:
    def __init__(self, dbpath):
        import sqlite3
        self.dbconnection = sqlite3.connect(dbpath, check_same_thread=False)
        self.dbconnection.row_factory = sqlite3.Row

    def query(self, * args, ** kwargs):
        #https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.execute
        if len(args) == 2:
            cursor = self.dbconnection.execute(args[0], args[1])
        else:
            cursor = self.dbconnection.execute(args[0])

        if cursor.rowcount != -1:
            return cursor.rowcount
        else:
            return cursor.fetchall()


    def commit(self):
        return self.dbconnection.commit()
