import schedule
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import psutil


"""
cron_manager.py

This centralized cron manager script schedules and runs periodic tasks
for the IoT energy monitoring pipeline using the `schedule` module.

Key responsibilities:
- Launch sensor simulation script every 30 seconds
- Aggregate CSV data into Parquet every 1 minute
- Upload aggregated data to MySQL every 1 minute
- Upload latest readings to ThingSpeak cloud every 1 minute
- Avoid concurrent executions using psutil-based overlap protection
- Log all events to logs/cron_manager.log

Designed to be run as a long-lived background process (manually or via systemd/cron).
"""


# ------------------------------
# CONFIGURATION
# ------------------------------

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "cron_manager.log"

# ------------------------------
# LOGGING SETUP
# ------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def log(msg):
    logging.info(msg)

def log_error(msg):
    logging.error(msg)

# ------------------------------
# SCRIPT EXECUTION UTILITIES
# ------------------------------

def is_script_running(script_name: str) -> bool:
    """
    Check if a given script is already running.

    Uses psutil to prevent overlapping executions of the same Python script.
    Returns True if the script is found in the current process list.
    """
    """Check if the given script is already running via psutil."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and script_name in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def run_script(script_path: str):
    """
    Execute a Python script via subprocess with overlap protection.

    Logs execution attempts and any errors that occur during invocation.
    Skips execution if script is already running.
    """
    """Run a script with overlap protection and logging."""
    if is_script_running(script_path):
        log(f"Skipping {script_path} (already running)")
        return
    try:
        log(f"Executing {script_path}")
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        log_error(f"Error running {script_path}: {e}")

# ------------------------------
# SCHEDULED TASKS
# ------------------------------

def generate_data():
    """Scheduled wrapper for sensor data generation."""
    run_script("scripts/generate_sample_data.py")

def aggregate_data():
    """Scheduled wrapper for aggregating recent CSVs to Parquet."""
    run_script("scripts/aggregate_parquet.py")

def upload_to_sql():
    """Scheduled wrapper for uploading latest Parquet to SQL."""
    run_script("scripts/upload_to_sql.py")

def upload_to_thingspeak():
    """Scheduled wrapper for uploading latest readings to ThingSpeak."""
    run_script("scripts/upload_thingspeak.py")

# ------------------------------
# JOB REGISTRATION
# ------------------------------

schedule.every(30).seconds.do(generate_data)
schedule.every(1).minutes.do(aggregate_data)
schedule.every(1).minutes.do(upload_to_sql)
schedule.every(1).minutes.do(upload_to_thingspeak)

log("Cron Manager started. Scheduling all jobs.")

# ------------------------------
# MAIN LOOP
# ------------------------------

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    log("Cron Manager stopped by user.")
