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
    metrics_df = df.groupby("player", as_index=False).agg(
        avg_points=("points", "mean"),
        avg_assists=("assists", "mean"),
        avg_rebounds=("rebounds", "mean"),
        games_played=("game_date", "nunique"),
        total_points=("points", "sum")
    )

    # add a ppg (points per game) column
    metrics_df['points_per_game'] = metrics_df['total_points'] / metrics_df['games_played'].replace(0, pd.NA) # protect against division by 0 although shouldnt really happen

    return metrics_df

def return_top_scorers(df: pd.DataFrame, top_n: int) -> pd.DataFrame:
    if top_n <= 0:
        return df.head(0)  # return empty DataFrame for non-positive top_n
    top_scorers_df = df.sort_values(by='points_per_game', ascending=False).head(top_n)
    return top_scorers_df

def validate_inputs(df: pd.DataFrame):
    required_columns = {'player', 'points', 'assists', 'rebounds', 'game_date'}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Input DataFrame is missing required columns: {missing}")
    
    

if __name__ == "__main__":
    file_path = "datasets/player_stats.csv"
    raw_data = load_data(file_path) # get the raw data
    df_clean = clean_data(raw_data) # we want to clean up the raw data first
    metrics_df = calculate_metrics(df_clean) # pass the cleaned data into metrics calculation
    top_3_summary = return_top_scorers(metrics_df, 3) # get top 3 scorers

    # print(raw_data)
    # print(df_clean)
    print(metrics_df)   
    print(top_3_summary)