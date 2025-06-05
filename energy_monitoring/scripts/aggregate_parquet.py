import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

"""
aggregate_parquet.py

This script scans the raw CSV data generated over the last 30 minutes and aggregates
it into a single Parquet file for compressed archival and efficient downstream processing.

- Reads raw CSV files from the data/raw/YYYY-MM-DD/ directory
- Filters only those CSVs created within the last 30 minutes
- Concatenates them into a single DataFrame
- Saves the DataFrame to data/processed/YYYY-MM-DD_HH-MM.parquet
- Deletes the original CSVs once the parquet is successfully written

Designed for low-power Raspberry Pi environments running scheduled tasks (via cron).
"""


# ---------------------------
# Logging Setup
# ---------------------------
LOG_FILE = Path(__file__).parent.parent / "logs" / "aggregate_parquet.log"
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def log(msg): logging.info(msg)
def log_error(msg): logging.error(msg)

# ---------------------------
# Paths and Constants
# ---------------------------
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------
# Main Function
# ---------------------------
def aggregate_recent_csv():
    """
    Aggregate all CSV files from the last 30 minutes into a Parquet file.

    This function:
    - Scans today's raw data directory
    - Filters CSV files created within the last 30 minutes (based on filename timestamps)
    - Reads and concatenates their contents
    - Saves a Parquet file in data/processed/
    - Deletes the original raw CSVs that were included in the aggregation
    """
    now = datetime.utcnow()
    start_time = now - timedelta(minutes=30)
    today_dir = RAW_DIR / now.strftime("%Y-%m-%d")

    if not today_dir.exists():
        log("No raw data directory for today.")
        return

    csv_files = sorted(today_dir.glob("*.csv"))
    used_files = []
    dfs = []

    for file in csv_files:
        try:
            file_time = datetime.strptime(file.stem, "%H-%M-%S")
            file_datetime = datetime.combine(now.date(), file_time.time())
        except ValueError:
            log_error(f"Skipping file with unexpected name format: {file}")
            continue

        if start_time <= file_datetime <= now:
            try:
                df = pd.read_csv(file)
                dfs.append(df)
                used_files.append(file)
            except Exception as e:
                log_error(f"Failed to read {file}: {e}")

    if not dfs:
        log("No CSVs to aggregate for this interval.")
        return

    aggregated_df = pd.concat(dfs, ignore_index=True)
    parquet_file = PROCESSED_DIR / f"{now.strftime('%Y-%m-%d_%H-%M')}.parquet"
    try:
        aggregated_df.to_parquet(parquet_file, index=False)
        log(f"Saved aggregated parquet: {parquet_file.name}")
    except Exception as e:
        log_error(f"Failed to write parquet: {e}")
        return

    # Delete used CSV files
    for file in used_files:
        try:
            os.remove(file)
            log(f"Deleted: {file.name}")
        except Exception as e:
            log_error(f"Could not delete {file.name}: {e}")

# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    aggregate_recent_csv()
