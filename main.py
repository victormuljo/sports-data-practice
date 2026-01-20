import json
import argparse
from pathlib import Path
from src.db import get_db_connection, read_sql_df
from src.ingest import ingest_csv

DB_PATH = 'databases/sports.db'
DATASET_DIR = Path('datasets')
TABLE_NAME = 'player_games'

def find_csv_files(datasets_dir: Path) -> list[str]:
    if not datasets_dir.exists():
        raise FileNotFoundError(f"Datasets folder not found: {datasets_dir}")
    return [str(p) for p in sorted(datasets_dir.glob("*.csv"))]

# check after ingestion
def post_ingest_checks(db_path: str, table_name: str) -> dict:
    with get_db_connection(db_path) as conn:
        # sanity check: count rows
        count_df = read_sql_df(f"SELECT COUNT(*) as n FROM {table_name};", conn)
        n = int(count_df["n"].iloc[0])
        
        # quality check: check for negative values
        neg = {}
        for col in ["points", "assists", "rebounds"]:
            neg_df = read_sql_df(f"SELECT COUNT(*) as n FROM {table_name} WHERE {col} < 0;", conn)
            neg[col] = int(neg_df['n'].iloc[0])

        # last updated
        last_df = read_sql_df(f"SELECT MAX(game_date) as last_updated FROM {table_name};", conn)
        last_updated = last_df['last_updated'].iloc[0]

    return {
        "rows_in_db": n,
        "negative_points_rows": neg["points"],
        "negative_assists_rows": neg["assists"],
        "negative_rebounds_rows": neg["rebounds"],
        "last_updated": last_updated
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["upsert", "replace"], default="upsert")
    parser.add_argument("--table", default=TABLE_NAME)
    args = parser.parse_args()

    csv_files = find_csv_files(DATASET_DIR)

    df_clean, validation_report, inserted, ingestion_report = ingest_csv(
        db_path=DB_PATH, 
        file_paths=csv_files, 
        table_name=args.table, 
        mode=args.mode
    )

    checks = post_ingest_checks(DB_PATH, args.table)

    print("\n=== INGESTION REPORT ===")
    print(json.dumps(ingestion_report, indent=2, default=str))

    print("\n=== VALIDATION REPORT ===")
    print(json.dumps(validation_report, indent=2, default=str))

    print("\n=== POST INGESTION REPORT ===")
    print(json.dumps(checks, indent=2, default=str))

    # hard fail if data quality is broken
    if any(checks[k] > 0 for k in ["negative_points_rows", "negative_assists_rows", "negative_rebounds_rows"]):
        raise ValueError("Post-ingest check failed: negative values found.")


    