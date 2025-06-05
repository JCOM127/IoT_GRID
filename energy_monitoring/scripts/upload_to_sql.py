import os
import logging
import pandas as pd
import pymysql
from pathlib import Path
from datetime import datetime


"""
upload_to_sql.py

Reads the latest Parquet file containing sensor data and uploads its contents
into the MySQL database, avoiding duplicates based on (Sensor_ID, Timestamp).

Steps:
- Reads the most recent .parquet file in the data/processed/ directory
- Maps (project_name, sensor_code) to Sensor_ID using the Sensors table
- Verifies for duplicate entries in Sensor_Data table
- Inserts only new rows for each sensor
- Skips any rows with invalid mappings or missing values

This script is intended to be triggered every 30 or 60 minutes via cron_manager.py.
"""


# --------------------------
# Logging Setup
# --------------------------
LOG_FILE = Path(__file__).parent.parent / "logs" / "upload_to_sql.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

log = logging.info
log_error = logging.error

# --------------------------
# MySQL Connection Config
# --------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Grid2030.", 
    "database": "energy_monitoring"
}

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

# --------------------------
# Get Latest Parquet File
# --------------------------
def get_latest_parquet_file():
    """
    Finds the most recent .parquet file from the processed data directory.

    Returns:
        Path or None: Path to the latest file, or None if no files exist
    """
    parquet_files = sorted(PROCESSED_DIR.glob("*.parquet"), reverse=True)
    return parquet_files[0] if parquet_files else None

# --------------------------
# Fetch Sensor Map
# --------------------------
def fetch_sensor_ids(conn):
    """
    Build a mapping from (project_name, sensor_code) to Sensor_ID.

    Args:
        conn (Connection): MySQL connection

    Returns:
        dict: {(project_name, sensor_code): sensor_id}
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.Sensor_ID, p.Project_Name, s.Sensor_Code
        FROM Sensors s
        JOIN Projects p ON s.Project_ID = p.Project_ID
    """)
    rows = cursor.fetchall()
    return {
    (proj_name.strip(), sensor_code.strip()): sid
    for (sid, proj_name, sensor_code) in rows
}

# --------------------------
# Fetch Existing Records
# --------------------------
def fetch_existing_records(conn):
    """
    Get all (Sensor_ID, Timestamp) combinations already present in the DB.

    Args:
        conn (Connection): MySQL connection

    Returns:
        set: Set of (sensor_id, timestamp) tuples
    """
    cursor = conn.cursor()
    cursor.execute("SELECT Sensor_ID, Timestamp FROM Sensor_Data")
    return set(cursor.fetchall())

# --------------------------
# Upload Logic
# --------------------------
def upload_parquet_to_sql():
    """
    Main uploader function. Reads latest Parquet data, checks for valid sensors,
    skips duplicates, and inserts new sensor readings into the SQL database.
    """
    latest_file = get_latest_parquet_file()
    if not latest_file:
        log("No Parquet file found.")
        return

    log(f"Processing: {latest_file.name}")
    df = pd.read_parquet(latest_file)

    required_cols = {"timestamp", "project_id", "sensor_id", "value"}
    if not required_cols.issubset(df.columns):
        log_error(f"Missing required columns in parquet: {df.columns}")
        return
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sensor_map = fetch_sensor_ids(conn)
        log(f"[DEBUG] sensor_map keys: {list(sensor_map.keys())[:10]}")
        existing = fetch_existing_records(conn)

        inserts = []
        for _, row in df.iterrows():
            key = (row["project_id"].strip(), row["sensor_id"].strip())
            sensor_id = sensor_map.get(key)

            if not sensor_id:
                log_error(f"Sensor not found: {key}")
                continue

            timestamp = pd.to_datetime(row["timestamp"]).to_pydatetime()
            value = float(row["value"])

            if (sensor_id, timestamp) in existing:
                continue  # Skip duplicates

            inserts.append((sensor_id, timestamp, value))

        if not inserts:
            log("No new records to insert.")
            return

        cursor.executemany(
            "INSERT INTO Sensor_Data (Sensor_ID, Timestamp, Value) VALUES (%s, %s, %s)",
            inserts
        )
        conn.commit()
        log(f"Inserted {cursor.rowcount} records.")
    except Exception as e:
        log_error(f"Upload failed: {e}")
    finally:
        if conn:
            conn.close()

# --------------------------
# Entrypoint
# --------------------------
if __name__ == "__main__":
    upload_parquet_to_sql()
