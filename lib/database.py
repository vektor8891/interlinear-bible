import sqlite3

import pandas as pd


def get_connection():
    import lib.globals

    con = sqlite3.connect(lib.globals.database_path)
    return con


def get_table(con: sqlite3.Connection, table: str):
    df = pd.read_sql_query(sql=f"SELECT * FROM {table}", con=con)
    return df
