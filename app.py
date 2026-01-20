import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from src.db import get_db_connection, read_sql_df


# Whitelist the columns for sorting to prevent SQL injection
SORT_COLUMNS = {
    "avg_points": "avg_points",
    "games_played": "games_played",
    "total_points": "total_points",
}

DB_PATH = 'databases/sports.db'

# Catch database error at start for streamlit
if not Path(DB_PATH).exists():
    st.error("Database not found. Run `python3 main.py` to generate it.")
    st.stop()

# --- Data caching to prevent repetivie data loading, store in the cache so its only ran once if nothing changes--- #
@st.cache_data
def get_last_updated(db_path: str) -> str:
    with get_db_connection(db_path) as conn: # guarantee data is closed properly
        df = read_sql_df("SELECT MAX(game_date) as last_updated FROM player_games;", conn)
    return df['last_updated'].iloc[0]

@st.cache_data
def get_player_metrics(db_path: str, sort_column: str, top_n: int) -> pd.DataFrame:
    sql_query = f"""
        SELECT player, ROUND(AVG(points), 1) as avg_points, COUNT(DISTINCT game_date) as games_played, SUM(points) as total_points
        FROM player_games
        GROUP BY player
        ORDER BY {sort_column} DESC
        LIMIT ?;
        """
    with get_db_connection(db_path) as conn:
        return read_sql_df(sql_query, conn, params=[top_n])

@st.cache_data
def get_player_list(db_path: str) -> list[str]:
    with get_db_connection(db_path) as conn:
        df = read_sql_df("SELECT DISTINCT player FROM player_games ORDER BY player ASC;", conn)
    return df['player'].tolist()

@st.cache_data
def get_player_game_log(db_path: str, player: str) -> pd.DataFrame:
    sql_query = """
            SELECT team, game_date, points, assists, rebounds
            FROM player_games
            WHERE player = ?
            ORDER BY game_date DESC;
            """
    with get_db_connection(db_path) as conn:
        return read_sql_df(sql_query, conn, params=[player])
    
@st.cache_data
def get_player_aggregate_metrics(db_path: str, player: str) -> pd.DataFrame:
    player_query_metrics = """ SELECT player, ROUND(AVG(points), 1) as avg_points, COUNT(DISTINCT game_date) as games_played, SUM(points) as total_points
            FROM player_games
            WHERE player = ?
            GROUP BY player;
            """
    with get_db_connection(db_path) as conn:
        return read_sql_df(player_query_metrics, conn, params=[player])

st.title("Sports Data Metrics Viewer")
st.markdown("See basic player analysis metrics stored in the database.")
st.caption("To refresh the database, run: `python3 main.py` in the terminal.")
if st.button("Refresh UI (clear cache)"):
    st.cache_data.clear()
    st.rerun()

try:
    # Show last updated
    last_updated = get_last_updated(DB_PATH)
    if last_updated is None:
        st.info("Database is empty. Run 'python3 main.py' to create and populate the database first.")
        st.stop()

    st.markdown(f"**Database last updated on:** {last_updated}")

    st.divider()

    # Top N and sorting selection
    top_n_value = st.slider("Number of top scorers to display", min_value=3, max_value=25, value=3, key="top_n") # slider for top N
    selected_sort = st.selectbox("Sort by:", options=["avg_points", "games_played", "total_points"], index=0, key="sort_by") # selectbox for sorting criteria

    sort_column = SORT_COLUMNS[selected_sort]

    # sql query to get average ppg, parameterized to prevent SQL injection
    sql_metrics_df = get_player_metrics(DB_PATH, sort_column, top_n_value)  # read metrics from the database
    st.dataframe(sql_metrics_df)
    st.bar_chart(sql_metrics_df, x='player', y=sort_column, horizontal=True) # top N bar chart

    st.divider()

    # Player selection for detailed view
    player_list = get_player_list(DB_PATH)
    if not player_list:
        st.info("No players found in the database. Run 'python3 main.py' to create and populate the database first.")
        st.stop()
    selected_player = st.selectbox("Select a player for detailed stats:", options=player_list, key="player_select")
    if selected_player:
        # Get player metrics
        player_metrics_df = get_player_aggregate_metrics(DB_PATH, selected_player)
        st.subheader(f"Aggregate Metrics for {selected_player}")
        st.dataframe(player_metrics_df, hide_index=True)

        # get player game log
        player_stats_df = get_player_game_log(DB_PATH, selected_player)
        player_stats_df['game_date'] = pd.to_datetime(player_stats_df['game_date'])  # ensure game_date is datetime
        player_stats_df["game_date_label"] = player_stats_df["game_date"].dt.strftime("%m/%d/%Y")
        st.subheader(f"Game Stats for {selected_player}")
        st.dataframe(player_stats_df[["team", "game_date_label", "points", "assists", "rebounds"]], hide_index=True)

        st.line_chart(player_stats_df.sort_values(by='game_date'), x='game_date_label', y=['points', 'assists', 'rebounds']) # player game log chart

    st.divider()

# we need to check for special case if table doesnt exist yet
except sqlite3.OperationalError as e:
    msg = str(e).lower()

    if "no such table" in msg:
        st.error("Database table 'player_games' does not exist. Run 'python3 main.py' to create and populate the database first.")
        st.stop()
    
    if "unable to open database file" in msg:
        st.error("Could not open the database file. Check the DB path and permissions.")
        st.stop()

    st.error(f"Database operational error: {e}")
    st.stop()
except sqlite3.Error as e:
    st.error(f"Error connecting to database. Run 'python3 main.py' to create and populate the database first: {e}")
    st.stop()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

