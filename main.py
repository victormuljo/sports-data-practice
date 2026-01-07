import json
from src.data import load_data, clean_data
from src.validation import validate_input
from src.metrics import calculate_metrics, return_top_scorers
from src.db import get_db_connection, write_df_to_table, read_sql_df

if __name__ == "__main__":
    file_path = "datasets/player_stats.csv"
    
    raw_data = load_data(file_path) # get the raw data
    validation_report = validate_input(raw_data) # validate the raw data
    df_clean = clean_data(raw_data) # we want to clean up the raw data first
    print("Cleaned data preview:\n", df_clean.head())

    sql_conn = get_db_connection('databases/sports.db')  # connect to the database
    write_df_to_table(df_clean, sql_conn, "player_games")  # write cleaned data to the database
    
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

    