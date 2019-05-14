from libs.db import Database

_instance = None

def instance(dbpath=None, autocommit=False):
    global _instance
    if not _instance:
        if dbpath:
            _instance = Database(dbpath, autocommit)
            print("Database connected")
        else:
            raise ValueError("No database connection.")
    return _instance