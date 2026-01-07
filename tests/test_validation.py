import pandas as pd
from src.validation import validate_input
import json

# valid dataframe
df_valid = pd.DataFrame({
    'player': ['LeBron James', 'Anthony Davis', 'Stephen Curry'],
    'team': ['LAL', 'LAL', 'GSW'],
    'points': [28, 22, 35],
    'assists': [8, 3, 6],   
    'rebounds': [7, 12, 5],
    'game_date': ['2024-03-01', '2024-03-01', '2024-03-02']
})

# missing required column, rebounds intentionally left out
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

df_whitespace = pd.DataFrame({
    'player': ['A', 'B'],
    'team': ['X', 'Y'],
    'points': [' 10 ', 20],
    'assists': [1, 2],   
    'rebounds': [3, 4],
    'game_date': ['2024-01-01', '2024-01-02']
})

def run_validation_test(name, df, expected_exception=None):

    # test the validation
    try:
        # validate the input. Test passes if no exception is raised when none expected, or if the expected exception is raised.
        input = validate_input(df)
        if expected_exception:
            print(f"Test {name}: FAILED (expected exception {expected_exception.__name__})")
        else:
            print(f"Test {name}: PASSED")
            print(json.dumps(input, indent=2, default=str))  # print the validation output for inspection
    except Exception as e:
        err_name = type(e).__name__
        if expected_exception and isinstance(e, expected_exception):
            print(f"Test {name}: PASSED (caught expected exception: {err_name}: {e})")
        else:
            print(f"Test {name}: FAILED (unexpected exception: {err_name}: {e})")

# Run tests
if __name__ == "__main__":
    run_validation_test("Valid DataFrame", df_valid) # should pass with no exception
    run_validation_test("Missing Required Column", df_missing_column, ValueError) # should pass with ValueError exception
    run_validation_test("Non-Numeric in Numeric Column", df_non_numeric, TypeError) # should pass with TypeError exception
    run_validation_test("Unparseable Date in game_date", df_unparseable_date, TypeError) # should pass with TypeError exception
    run_validation_test("Duplicate Record", df_dupe, ValueError)   # should pass with ValueError exception
    run_validation_test("Whitespace Handling", df_whitespace) # should pass with no exception  