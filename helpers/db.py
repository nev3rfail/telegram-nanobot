from libs.db import Database

_instance = None

def instance(dbpath=None):
    global _instance
    if not _instance:
        if dbpath:
            _instance = Database(dbpath)
            print("Database connected")
        else:
            raise ValueError("No database connection.")
    return _instance