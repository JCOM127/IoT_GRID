# File: tests/test_core_pipeline.py

import os
import json
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config" / "sensor_config.json"
RAW_DIR = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"

# ----------
# Helpers
# ----------

def most_recent_file(folder: Path, ext: str):
    files = sorted(folder.glob(f"*.{ext}"), reverse=True)
    return files[0] if files else None

# ----------
# Tests
# ----------

def test_sensor_config_loads():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    assert isinstance(config, list)
    assert all("sensor_id" in s for s in config)

def test_csv_generated():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    folder = RAW_DIR / today
    assert folder.exists(), "Raw folder does not exist. Run generate_sample_data.py first."
    csv = most_recent_file(folder, "csv")
    assert csv and csv.exists(), "No CSV file found."
    df = pd.read_csv(csv)
    assert not df.empty and "sensor_id" in df.columns

def test_parquet_created():
    parquet = most_recent_file(PROC_DIR, "parquet")
    assert parquet and parquet.exists(), "No Parquet file found. Run aggregate_parquet.py first."
    df = pd.read_parquet(parquet)
    assert not df.empty and "value" in df.columns

def test_upload_sql_success():
    # Placeholder: simply test that upload script runs without exception
    # Could be expanded with mock DB
    from scripts import upload_to_sql
    upload_to_sql.upload_parquet_to_sql()

def test_upload_thingspeak_runs():
    # Placeholder: test function runs (use a dummy API key in config)
    from scripts import upload_thingspeak
    upload_thingspeak.upload_to_thingspeak()
