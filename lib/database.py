def get_connection():
    import sqlite3 as sl
    import lib.globals

    con = sl.connect(lib.globals.database_path)
    return con
