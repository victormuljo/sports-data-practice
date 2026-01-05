# Create the functions:
# load_data() 
# clean_data(df) 
# calculate_metrics(df)

import pandas as pd

# load player stats from csv file
def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df

def validate_inputs(df: pd.DataFrame):

    # required columns check
    required_columns = {'player', 'points', 'assists', 'rebounds', 'game_date'}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Input DataFrame is missing required columns: {missing}")
    
    # check datatypes
    # points, assists, and rebounds should be numeric (should brush over missing values here)
    for col in ['points', 'assists', 'rebounds']:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise TypeError(f"Column '{col}' must be numeric.")

    # game_date should be of date time format so it can be converted into datetime later
    # 1) it must exist
    # 2) it must be parseable as a datetime type
    # 3) reasonable date range
    if not pd.api.types.is_datetime64_any_dtype(df['game_date']):
        # Parse to check convertibility without mutating the original column.
        # Important: ignore missing values here; they'll be validated separately below.
        non_missing_mask = df['game_date'].notna()
        parsed = pd.to_datetime(df.loc[non_missing_mask, 'game_date'], format='mixed', errors='coerce')
        if parsed.isna().any():
            raise TypeError("Column 'game_date' contains unparseable non-null date values.")
        if parsed.dt.year.max() > pd.Timestamp.now().year:
            raise ValueError("Column 'game_date' contains dates in the future.")
    

    # count missing values in player, points, and game_date
    # which are allowed? which should fail the run?
    # - player should not have missing values
    # - points can be missing (we handle that in cleaning)
    # - game_date should not have missing values
    if df['player'].isnull().any():
        player_null_count = df['player'].isnull().sum()
        raise ValueError(f"Column 'player' contains {player_null_count} missing values.")
    if df['points'].isnull().any():
        points_null_count = df['points'].isnull().sum()
        print(f"Warning: column 'points' contains {points_null_count} missing values.")
        pass # allowed, will be handled in cleaning
    if df['game_date'].isnull().any():
        game_date_null_count = df['game_date'].isnull().sum()
        raise ValueError(f"Column 'game_date' contains {game_date_null_count} missing values.")
    
    # detect duplicate game records using playuer and game_date
    duplicates = df.duplicated(subset=['player', 'game_date'])
    if duplicates.any():
        duplicates_count = duplicates.sum()
        raise ValueError(f"Input DataFrame contains {duplicates_count} duplicate game records for the same player on the same date.")
        # maybe it can raise a warning instead of error?

    print("Input DataFrame validation passed.")
    print("Number of records:", len(df))
    print("Number of unique players:", df['player'].nunique())
    print()

    return True

# clean and normalize player stats data
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()
    clean_df.columns = [ col.strip().lower() for col in clean_df.columns ] # normalize the columns
    clean_df["points"] = clean_df["points"].fillna(0) # fill missing points with 0
    clean_df["assists"] = clean_df["assists"].fillna(0) # fill missing assists with 0
    clean_df["rebounds"] = clean_df["rebounds"].fillna(0) # fill missing rebounds with 0
    clean_df["game_date"] = pd.to_datetime(clean_df["game_date"], format='mixed') # convert game_date to datetime

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


if __name__ == "__main__":
    file_path = "datasets/player_stats.csv"
    
    raw_data = load_data(file_path) # get the raw data
    validate_inputs(raw_data) # validate the raw data
    df_clean = clean_data(raw_data) # we want to clean up the raw data first
    
    metrics_df = calculate_metrics(df_clean) # pass the cleaned data into metrics calculation
    top_3_summary = return_top_scorers(metrics_df, 3) # get top 3 scorers

    # validate_inputs(df_clean)
    # print(raw_data)
    # print(df_clean)
    print(metrics_df)   
    print(top_3_summary)