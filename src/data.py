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
    clean_df["game_date"] = pd.to_datetime(clean_df["game_date"]).dt.strftime("%Y-%m-%d %H:%M:%S") # convert game_date to datetime

    return clean_df