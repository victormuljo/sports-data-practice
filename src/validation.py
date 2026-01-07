import pandas as pd

# helper function to normalize the series
def normalize_str_series(series: pd.Series) -> pd.Series:
    return series.astype('string').str.strip().replace('', pd.NA)

def validate_input(df: pd.DataFrame):
    warnings = []

    # required columns check
    required_columns = {'player', 'points', 'assists', 'rebounds', 'game_date', 'team'}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(f"Input DataFrame is missing required columns: {missing}")
    
    # check datatypes
    # Numeric columns (points, assists, rebounds): allow nulls, but non-null values must be convertible to numbers.
    for col in ['points', 'assists', 'rebounds']:
        series = df[col]
        series_trimmed = normalize_str_series(series) # trim whitespace and treat empty strings as NA
        non_missing_mask = series_trimmed.notna() # mask of non-missing values
        coerced = pd.to_numeric(series_trimmed[non_missing_mask], errors='coerce') # temp convert to numeric
        bad_mask = coerced.isna() # check for the bad values that couldnt be converted
        if bad_mask.any():
            bad_values = series_trimmed[non_missing_mask][bad_mask] # get all the bad values
            examples = bad_values.unique()[:5] # get a small snippet of bad values
            raise TypeError(f"Column '{col}' contains non-numeric values: {examples}")

    # game_date should be of date time format so it can be converted into datetime later
    # 1) it must exist
    # 2) it must be parseable as a datetime type
    # 3) reasonable date range
    game_date_series = normalize_str_series(df['game_date']) # trim whitespace and treat empty strings as NA
    # Parse to check convertibility without mutating the original column.
    # Important: ignore missing values here; they'll be validated separately below.
    non_missing_mask = game_date_series.notna()
    parsed = pd.to_datetime(game_date_series[non_missing_mask], format='%Y-%m-%d', errors='coerce')
    if non_missing_mask.sum() == 0:
        raise ValueError("Column 'game_date' has no valid dates.")
    if parsed.isna().any():
        raise TypeError("Column 'game_date' contains unparseable non-null date values.")
    if (parsed < pd.Timestamp("1900-01-01")).any() or (parsed > pd.Timestamp.now()).any():
        raise ValueError("Column 'game_date' contains dates outside the reasonable range.")

    # FUTURE: team should be string type, but not enforced yet

    # count missing values in player, points, and game_date
    # - player should not have missing values
    # - points can be missing (we handle that in cleaning)
    # - game_date should not have missing values
    player_series = normalize_str_series(df['player'])
    if player_series.isna().any():
        player_null_count = player_series.isna().sum()
        raise ValueError(f"Column 'player' contains {player_null_count} missing values.")
    
    points_series = normalize_str_series(df['points'])
    if points_series.isna().any():
        points_null_count = points_series.isna().sum()
        warnings.append(f"Warning: column 'points' contains {points_null_count} missing values.") # allowed, will be handled in cleaning
        
    if game_date_series.isna().any():
        game_date_null_count = game_date_series.isna().sum()
        raise ValueError(f"Column 'game_date' contains {game_date_null_count} missing values.")
    
    # detect duplicate game records using playuer and game_date
    # this will be adjusted as project grows, this duplicate rule wont apply as new teams or game id will be applied as columns
    duplicates = df.duplicated(subset=['player', 'game_date', 'team'])
    duplicates_count = duplicates.sum()
    if duplicates.any():
        raise ValueError(f"Input DataFrame contains {duplicates_count} duplicate game records for the same player on the same date and same team")
        # maybe it can raise a warning instead of error?

    return {
        'records': len(df), 
        'unique_players': df['player'].nunique(), 
        'player_null_count': player_series.isna().sum(), 
        'points_null_count': points_series.isna().sum(), 
        'game_date_null_count': game_date_series.isna().sum(),
        'duplicates_count': duplicates_count,
        'warnings': warnings
        }
