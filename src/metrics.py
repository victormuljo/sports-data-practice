import pandas as pd

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
