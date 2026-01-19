import sqlite3
import pandas as pd
from pathlib import Path

# functions to interact with the SQLite database
# helper function to check if table exists:
def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    query = "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?"
    cursor = conn.execute(query, (table_name,))
    return cursor.fetchone() is not None

# 1. Function to create/connect to the database
def get_db_connection(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)  # ensure directory exists
    return sqlite3.connect(db_path)

# 2. Function to write DataFrames to SQLite tables
def write_df_to_table(df: pd.DataFrame, conn: sqlite3.Connection, table_name: str, mode: str, key_cols: list = None) -> int:
    if mode not in {"upsert", "replace"}:
        raise ValueError("Invalid mode. Mode must be either 'upsert' or 'replace'")
    
    if df.empty:
        return 0 # empty df, nothing to change
    
    if mode == "replace":
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        return len(df)
    
    if mode == "upsert":
        # checks first
        if not key_cols:
            raise ValueError("key_cols is required for upsert mode")
        missing = [c for c in key_cols if c not in df.columns]
        if missing:
            raise ValueError(f"df is missing key_cols required for upsert: {missing}")
        # ensure table exists
        if not table_exists(conn, table_name):
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            return len(df)
        
        # fetch existing keys from DB
        query = f"SELECT {', '.join(key_cols)} FROM {table_name};"
        existing_keys = pd.read_sql_query(query, conn)

        # dedupe within incoming batch
        df_incoming = df.drop_duplicates(subset=key_cols).copy()

        # Make sure key column dtypes match between incoming df and existing_keys
        for col in key_cols:
            if col in df_incoming.columns and col in existing_keys.columns:
                if col == "game_date":
                    df_incoming[col] = pd.to_datetime(df_incoming[col], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
                    existing_keys[col] = pd.to_datetime(existing_keys[col], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")

                    # Defensive: if anything couldn't parse, raise a clear error
                    if df_incoming[col].isna().any():
                        raise ValueError("Incoming df has unparseable game_date values during upsert key normalization.")
                    if existing_keys[col].isna().any():
                        raise ValueError("Database contains unparseable game_date values; consider rebuilding the table once (mode='replace').")
                else:
                    # normalize strings for keys like player/team
                    df_incoming[col] = df_incoming[col].astype("string").str.strip()
                    existing_keys[col] = existing_keys[col].astype("string").str.strip()

        # keep all incoming rows and filter for only new rows
        merged = df_incoming.merge(existing_keys, on=key_cols, how='left', indicator=True)
        df_new = merged[merged["_merge"] == "left_only"].drop(columns=['_merge'])


        # append only those rows
        if df_new.empty:
            return 0 # nothing new to insert
        
        df_new.to_sql(table_name, conn, if_exists="append", index=False)
        return len(df_new)

# 3. Function to run read-only queries and return results as DataFrames
def read_sql_df(query: str, conn: sqlite3.Connection, params=None) -> pd.DataFrame:
    return pd.read_sql_query(query, conn, params=params)

# Function to initialize DB to create a real schema
def init_db(conn: sqlite3.Connection, table_name: str = "player_games") -> None:
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY,
        player TEXT NOT NULL,
        team TEXT NOT NULL,
        points REAL,
        assists REAL,
        rebounds REAL,
        game_date TEXT NOT NULL,
        UNIQUE(player, team, game_date)
    );
    """

    create_index_player = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_player_date ON {table_name}(player, game_date);"
    create_index_team = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_team_date ON {table_name}(team, game_date);"

    conn.execute(create_table_query)

    print(f"Created table {table_name}")

    conn.execute(create_index_player)
    conn.execute(create_index_team)

    print(f"Created player and team game date indices for {table_name}")

