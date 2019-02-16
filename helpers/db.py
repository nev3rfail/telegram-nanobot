from libs.db import Database

_connection = None

def connection(dbpath=""):
    global _connection
    if not _connection:
        print("new connection")
        _connection = Database(dbpath)
    return _connection