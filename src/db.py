import sqlite3
import pandas as pd
from pathlib import Path

# functions to interact with the SQLite database
# 1. Function to create/connect to the database
def get_db_connection(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)  # ensure directory exists
    return sqlite3.connect(db_path)

# 2. Function to write DataFrames to SQLite tables
def write_df_to_table(df: pd.DataFrame, conn: sqlite3.Connection, table_name: str) -> None:
    df.to_sql(table_name, conn, if_exists='replace', index=False)

# 3. Function to run read-only queries and return results as DataFrames
def read_sql_df(query: str, conn: sqlite3.Connection, params=None) -> pd.DataFrame:
    return pd.read_sql_query(query, conn, params=params)