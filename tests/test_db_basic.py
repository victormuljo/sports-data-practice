import pandas as pd
from src.db import get_db_connection, write_df_to_table, read_sql_df

# valid dataframe
df_valid = pd.DataFrame({
    'player': ['LeBron James', 'LeBron James', 'Anthony Davis', 'Stephen Curry'],
    'team': ['LAL', 'LAL', 'LAL', 'GSW'],
    'points': [26, 22, 35, 30],
    'assists': [8, 3, 6, 7],   
    'rebounds': [7, 12, 5, 4],
    'game_date': ['2024-03-01', '2025-03-21', '2024-03-02', '2024-03-02']
})

if __name__ == "__main__":

    sql_conn = get_db_connection('databases/test_sports.db')  # connect to the database
    write_df_to_table(df_valid, sql_conn, "test_player_games") # write cleaned data to the database

    sql_query = """
        SELECT player, AVG(points) as avg_points, COUNT(DISTINCT game_date) as games_played, SUM(points) as total_points
        FROM test_player_games
        GROUP BY player
        ORDER BY total_points DESC;
    """

    sql_metrics_df = read_sql_df(sql_query, sql_conn)  # read metrics from the database


    sql_conn.close()  # close the database connection
    
    # if numbers were wrong in production, would users notice? If yes, assert it. If no, not really worth asserting
    assert len(sql_metrics_df) == 3  # we have 3 unique players
    assert sql_metrics_df.iloc[0]['player'] == 'LeBron James'  # top scorer should be LeBron
    assert sql_metrics_df[sql_metrics_df['player'] == 'LeBron James']['games_played'].iloc[0] == 2  # lebrons games played should be 2
    assert sql_metrics_df[sql_metrics_df['player'] == 'LeBron James']['total_points'].iloc[0] == 48  # LeBron total points should be 48

    print("PASSED")