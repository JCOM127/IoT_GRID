"""
generate_sample_data.py

This script simulates sensor readings and writes them to a timestamped CSV file
within a date-organized folder (data/raw/YYYY-MM-DD/).

- Reads sensor definitions from config/sensor_config.json
- Randomly generates realistic values per sensor type
- Writes one row per sensor every time it runs
- CSV file includes: timestamp, project_id, sensor_id, sensor_type, value, unit

Intended to be run on a schedule (e.g., every 30 seconds via cron or scheduler).
"""

import csv
import random
import time
from datetime import datetime
from pathlib import Path
import json

# Path to sensor configuration file (sensor IDs, types, units)
CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'sensor_config.json'
RAW_DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'

# Load sensor configuration
with open(CONFIG_PATH, 'r') as f:
    SENSOR_CONFIG = json.load(f)

# Simulate a reading for a given sensor type
def simulate_value(sensor_type):
    """
    Generate a realistic random value based on sensor type.

    Parameters:
        sensor_type (str): One of the known types defined in SENSOR_CONFIG.

    Returns:
        float: Randomly generated value within expected operating range.
    """
    ranges = {
        'temperature': (20.0, 40.0),
        'voltage': (10.0, 24.0),
        'current': (0.1, 5.0),
        'irradiance': (200.0, 1000.0),
        'wind_speed': (0.0, 20.0),
        'wind_direction': (0, 360),
        'pressure': (100000, 400000),
        'power': (0.0, 2000.0),
    }
    lo, hi = ranges.get(sensor_type, (0, 1))
    return round(random.uniform(lo, hi), 2)

def generate_sample():
    """
    Simulate one full reading cycle for all configured sensors and write to CSV.

    Output:
        A new CSV file saved under data/raw/YYYY-MM-DD/HH-MM-SS.csv,
        containing a row per sensor at the same UTC timestamp.
    """
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
    today = datetime.utcnow().strftime('%Y-%m-%d')
    raw_folder = RAW_DATA_DIR / today
    raw_folder.mkdir(parents=True, exist_ok=True)

    filename = f"{datetime.utcnow().strftime('%H-%M-%S')}.csv"
    filepath = raw_folder / filename

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'project_id', 'sensor_id', 'sensor_type', 'value', 'unit'])
        for sensor in SENSOR_CONFIG:
            value = simulate_value(sensor['sensor_type'])
            writer.writerow([
                timestamp,
                sensor['project_id'],
                sensor['sensor_id'],
                sensor['sensor_type'],
                value,
                sensor['unit']
            ])

    print(f"[INFO] Sample data written to {filepath}")

if __name__ == '__main__':
    generate_sample()
