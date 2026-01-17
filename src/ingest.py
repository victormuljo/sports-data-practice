# this will load csvs, validate the data, clean, and write to SQLite
import pandas as pd
from pathlib import Path
from src.data import clean_data
from src.validation import validate_input, validate_path
from src.db import get_db_connection, write_df_to_table

# this should ingest multiple csv files before writing to sqlite
def ingest_csv(db_path: str, file_paths: list[str], table_name: str = "player_games"):
    # check file paths
    for file in file_paths:
        validate_path(file)

    # load csvs
    df_raw = pd.concat(map(pd.read_csv, file_paths), ignore_index=True)

    # validate raws
    validation_report = validate_input(df_raw)

    # clean
    all_df_clean = clean_data(df_raw)

    # write to sqlite
    with get_db_connection(db_path) as conn:
        write_df_to_table(all_df_clean, conn, table_name)

    # return the clean df
    return all_df_clean, validation_report