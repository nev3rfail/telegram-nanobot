from libs.db import Database

_connection = None

def connection(dbpath=None):
    global _connection
    if not _connection:
        if dbpath:
            _connection = Database(dbpath)
            print("Database connected")
        else:
            raise ValueError("No database connection.")
    return _connection