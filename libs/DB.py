
import threading
lock = threading.Lock()
class DB:
    def __init__(self, dbpath):
        import sqlite3
        self.dbconnection = sqlite3.connect(dbpath, check_same_thread=False)
        self.dbconnection.row_factory = sqlite3.Row
        self.dbcursor = self.dbconnection.cursor()

    def query(self, * args, ** kwargs):
        if len(args) == 2:
            try:
                lock.acquire(True)
                self.dbcursor.execute(args[0], args[1])
            finally:
                lock.release()
        else:
            try:
                lock.acquire(True)
                self.dbcursor.execute(args[0])
            finally:
                lock.release()

        #if 'debug' in kwargs:
            #print pprint(self.dbcursor.description, indent=10, depth=10)
            #print self.dbcursor.rowcount
            #print self.dbcursor.rownumber
        if self.dbcursor.rowcount != -1:
            return self.dbcursor.rowcount
        else:
            return self.dbcursor.fetchall()


    def commit(self):
        return self.dbconnection.commit()
