import pandas as pd

# valid dataframe
df_valid = pd.DataFrame({
    'player': ['LeBron James', 'Anthony Davis', 'Stephen Curry'],
    'team': ['LAL', 'LAL', 'GSW'],
    'points': [28, 22, 35],
    'assists': [8, 3, 6],   
    'rebounds': [7, 12, 5],
    'game_date': ['2024-03-01', '2024-03-01', '2024-03-02']
})

# missing required column
df_missing_column = pd.DataFrame({
    'player': ['LeBron James', 'Anthony Davis', 'Stephen Curry'],
    'team': ['LAL', 'LAL', 'GSW'],
    'points': [28, 22, 35],
    'assists': [8, 3, 6],   
    'game_date': ['2024-03-01', '2024-03-01', '2024-03-02']
})

# non-numeric in numeric column
df_non_numeric = pd.DataFrame({
    'player': ['LeBron James', 'Anthony Davis', 'Stephen Curry'],
    'team': ['LAL', 'LAL', 'GSW'],
    'points': [45, 'abc', 35],
    'assists': [8, 3, 6],   
    'rebounds': [7, 12, 5],
    'game_date': ['2024-03-01', '2024-03-01', '2024-03-02']
})

# unparseable date in game_date
df_unparseable_date = pd.DataFrame({
    'player': ['LeBron James', 'Anthony Davis', 'Stephen Curry'],
    'team': ['LAL', 'LAL', 'GSW'],
    'points': [28, 22, 35],
    'assists': [8, 3, 6],   
    'rebounds': [7, 12, 5],
    'game_date': ['invalid-date', '2024-03-01', '2024-03-02']
})

# duplicate record
df_dupe = pd.DataFrame({
    'player': ['LeBron James', 'LeBron James', 'Stephen Curry'],
    'team': ['LAL', 'LAL', 'GSW'],
    'points': [28, 22, 35],
    'assists': [8, 3, 6],   
    'rebounds': [7, 12, 5],
    'game_date': ['2024-03-01', '2024-03-01', '2024-03-02']
})
