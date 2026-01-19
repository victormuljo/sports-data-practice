import json
import os
from pathlib import Path
from src.data import load_data, clean_data
from src.validation import validate_input
from src.metrics import calculate_metrics, return_top_scorers
from src.db import get_db_connection, write_df_to_table, read_sql_df
from src.ingest import ingest_csv


DB_PATH = 'databases/sports_test.db'
DATASET_DIR = Path('datasets')
TABLE_NAME = 'player_games'

if __name__ == "__main__":
    csv_files = list(DATASET_DIR.glob("*.csv"))

    df_clean, validation_report, inserted = ingest_csv(DB_PATH, csv_files, TABLE_NAME)

    sql_conn = get_db_connection(DB_PATH)  # connect to the database

    metrics_df = calculate_metrics(df_clean) # pass the cleaned data into metrics calculation
    top_3_summary = return_top_scorers(metrics_df, 3) # get top 3 scorers

    # sql query to get average ppg
    sql_query = """
    SELECT player, AVG(points) as avg_points, COUNT(DISTINCT game_date) as games_played, SUM(points) as total_points
    FROM player_games
    GROUP BY player
    ORDER BY avg_points DESC;
    """

    sql_metrics_df = read_sql_df(sql_query, sql_conn)  # read metrics from the database

    sql_conn.close()  # close the database connection

    # validate_inputs(df_clean)
    # print(raw_data)
    # print(df_clean)
    print("Validation report: ", json.dumps(validation_report, indent=2, default=str))
    print("\nPandas metrics:\n", metrics_df)

    print("\nTop 3 scorers (Pandas):\n", top_3_summary)
    print("\nSQL metrics:\n", sql_metrics_df)

    print(f"Inserted {inserted} new rows into {TABLE_NAME}")

    