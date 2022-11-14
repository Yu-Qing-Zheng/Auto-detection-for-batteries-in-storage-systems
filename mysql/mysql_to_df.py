from mysql.mysql_model import *
import pandas as pd

def mysql_to_df(table):
    sql = "select * from " + table
    df = pd.read_sql_query(sql, engine)
    return df