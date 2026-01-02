# Create the functions:
# load_data() 
# clean_data(df) 
# calculate_metrics(df)

import pandas as pd

# load player stats from csv file
def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df

# clean and normalize player stats data
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()
    clean_df.columns = [ col.strip().lower() for col in clean_df.columns ] # normalize the columns
    clean_df["points"] = clean_df["points"].fillna(0) # fill missing points with 0
    clean_df["assists"] = clean_df["assists"].fillna(0) # fill missing assists with 0
    clean_df["rebounds"] = clean_df["rebounds"].fillna(0) # fill missing rebounds with 0
    clean_df["game_date"] = pd.to_datetime(clean_df["game_date"]) # convert game_date to datetime

    return clean_df

# turn raw stats into aggregated metrics
def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # get average points, assists, rebounds and games played per player
    metrics_df = df.groupby("player").agg(
        avg_points=("points", "mean"),
        avg_assists=("assists", "mean"),
        avg_rebounds=("rebounds", "mean"),
        games_played=("game_date", "nunique")
    ).reset_index()
    return metrics_df

if __name__ == "__main__":
    file_path = "datasets/player_stats.csv"
    raw_data = load_data(file_path) # get the raw data
    clean_data_df = clean_data(raw_data) # we want to clean up the raw data first
    player_summary = calculate_metrics(clean_data_df) # pass the cleaned data into metrics calculation

    print(raw_data)
    print(clean_data_df)
    print(player_summary)   