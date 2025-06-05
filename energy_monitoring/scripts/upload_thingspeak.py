import json
import logging
import requests
import pandas as pd
import pymysql
from pathlib import Path
from datetime import datetime

"""
upload_thingspeak.py

Uploads the latest sensor readings from the MySQL database to the ThingSpeak cloud API.

- Loads sensor metadata and mapping from sensor_config.json and thingspeak_channels.json
- Retrieves the most recent value for each sensor from Sensor_Data table
- Groups sensors by project and prepares payloads using field mapping
- Sends an HTTP POST request to the appropriate ThingSpeak channel using API keys

This script is intended to be scheduled (e.g., every 5 or 10 minutes) via cron_manager.py.
"""
# ----------------------
# Logging Setup
# ----------------------
LOG_FILE = Path(__file__).parent.parent / "logs" / "upload_thingspeak.log"
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

# ----------------------
# MySQL Connection Config
# ----------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Grid2030.",
    "database": "energy_monitoring"
}

# ----------------------
# Load Config Files
# ----------------------
def load_sensor_config():
    """
    Load sensor metadata from config/sensor_config.json.

    Returns:
        list: List of sensor definition dictionaries with project_id, sensor_id, type, unit, and field.
    """
    config_file = Path(__file__).parent.parent / "config" / "sensor_config.json"
    with open(config_file, "r") as f:
        return json.load(f)

def load_thingspeak_config():
    """
    Load ThingSpeak API keys and field mappings from config/thingspeak_channels.json.

    Returns:
        dict: Mapping from project name to ThingSpeak API and field configuration.
    """
    config_path = Path(__file__).parent.parent / "config" / "thingspeak_channels.json"
    with open(config_path, "r") as f:
        return json.load(f)

# ----------------------
# Get Latest Value for Sensor
# ----------------------
def fetch_latest_value(conn, sensor_id):
    """
    Fetch the most recent reading for a given sensor from the database.

    Args:
        conn (pymysql.Connection): Open database connection
        sensor_id (int): Sensor ID

    Returns:
        float or None: The most recent value, or None if no record exists
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Value FROM Sensor_Data WHERE Sensor_ID = %s ORDER BY Timestamp DESC LIMIT 1",
        (sensor_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else None

# ----------------------
# Upload Logic
# ----------------------
def upload_to_thingspeak():
    """
    Load sensor values and upload them to the ThingSpeak API.

    This function:
    - Connects to the MySQL database
    - Maps (project, sensor_code) → Sensor_ID
    - Reads most recent values from Sensor_Data
    - Constructs ThingSpeak payloads by project
    - Sends updates to each channel via HTTP POST
    """
    sensor_configs = load_sensor_config()
    thingspeak_config = load_thingspeak_config()

    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Build mapping of Sensor_IDs by (project, sensor_code)
        cursor.execute("""
        SELECT s.Sensor_ID, p.Project_Name, s.Sensor_Code
        FROM Sensors s
        JOIN Projects p ON s.Project_ID = p.Project_ID
        """)
        rows = cursor.fetchall()
        sensor_map = {
        (proj_name.strip(), sensor_code.strip()): sensor_id
        for (sensor_id, proj_name, sensor_code) in rows
    }

        # Group sensors by project
        grouped = {}
        for sensor in sensor_configs:
            proj = sensor["project_id"]
            grouped.setdefault(proj, []).append(sensor)

        # Upload per project
        for project, sensors in grouped.items():
            ts_info = thingspeak_config.get(project)
            if not ts_info:
                log_error(f"No ThingSpeak config found for project: {project}")
                continue

            api_key = ts_info.get("write_api_key")
            field_map = ts_info.get("fields", {})
            payload = { "api_key": api_key }

            for s in sensors:
                key = (s["project_id"].strip(), s["sensor_id"].strip())
                sensor_id = sensor_map.get(key)

                if not sensor_id:
                    log_error(f"[{project}] Sensor not found in DB: {key}")
                    continue

                value = fetch_latest_value(conn, sensor_id)
                if value is None:
                    log_error(f"[{project}] No recent value found for: {key}")
                    continue

                field_name = field_map.get(s["sensor_id"])
                if not field_name:
                    log_error(f"[{project}] Field mapping not found for sensor: {s['sensor_id']}")
                    continue

                payload[field_name] = value

            # Log the full payload
            log(f"[{project}] Sending payload: {payload}")

            # POST to ThingSpeak
            try:
                response = requests.post("https://api.thingspeak.com/update", data=payload)
                if response.status_code == 200 and response.text != "0":
                    log(f"[{project}] Uploaded successfully. Entry ID: {response.text}")
                else:
                    log_error(f"[{project}] Upload failed. Status: {response.status_code}, Body: {response.text}")
            except Exception as e:
                log_error(f"[{project}] HTTP request error: {e}")

    except Exception as e:
        log_error(f"Database connection failed: {e}")
    finally:
        if conn:
            conn.close()

# ----------------------
# Entrypoint
# ----------------------
if __name__ == "__main__":
    upload_to_thingspeak()
