import pandas as pd
from src.data import load_data, clean_data
from src.validation import validate_input
from src.metrics import calculate_metrics, return_top_scorers

if __name__ == "__main__":
    file_path = "datasets/player_stats.csv"
    
    raw_data = load_data(file_path) # get the raw data
    validation_report = validate_input(raw_data) # validate the raw data
    df_clean = clean_data(raw_data) # we want to clean up the raw data first
    
    metrics_df = calculate_metrics(df_clean) # pass the cleaned data into metrics calculation
    top_3_summary = return_top_scorers(metrics_df, 3) # get top 3 scorers

    # validate_inputs(df_clean)
    # print(raw_data)
    # print(df_clean)
    print(validation_report)
    print(metrics_df)

    