import pandas as pd

# load player stats from csv file
def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df

# clean and normalize player stats data
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()
    clean_df.columns = [ col.strip().lower() for col in clean_df.columns ] # normalize the columns

    # convert numeric columns
    for col in ["points", "assists", "rebounds"]:
        clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce').fillna(0)

    # parse game date, check, then format
    parsed_date_time = pd.to_datetime(clean_df["game_date"], errors='coerce') # convert game_date to datetime
    if parsed_date_time.isna().any():
        bad_examples = clean_df.loc[parsed_date_time.isna(), "game_date"].astype("string").unique()[:5]
        raise ValueError(f"Dataframe has unparseable game_date values during date time key normalization. Examples: {bad_examples}")
    clean_df['game_date'] = parsed_date_time.dt.strftime("%Y-%m-%d %H:%M:%S")

    return clean_df