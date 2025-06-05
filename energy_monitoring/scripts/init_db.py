"""
init_db.py

Initializes the MySQL database schema for the energy monitoring system.

- Creates tables: Projects, Sensors, Sensor_Data, Power_Generation
- Connects to a running MySQL server using credentials from config
- Must be run manually once before starting the data pipeline

Note: Assumes the database 'energy_monitoring' already exists.
"""

import pymysql
import logging

# ---------------------------
# DB Configuration
# ---------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Grid2030.",
    "database": "energy_monitoring"
}

# ---------------------------
# SQL SCHEMA
# ---------------------------
SCHEMA_SQL = """
-- Projects table
CREATE TABLE IF NOT EXISTS Projects (
    Project_ID INT AUTO_INCREMENT PRIMARY KEY,
    Project_Name VARCHAR(100) NOT NULL,
    Source_Type ENUM('Solar', 'Wind', 'Hybrid', 'Other') NOT NULL,
    Location VARCHAR(255),
    Description TEXT,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sensors table
CREATE TABLE IF NOT EXISTS Sensors (
    Sensor_ID INT AUTO_INCREMENT PRIMARY KEY,
    Project_ID INT NOT NULL,
    Sensor_Code VARCHAR(50) NOT NULL,
    Sensor_Type VARCHAR(100) NOT NULL,
    Unit VARCHAR(50) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Project_ID) REFERENCES Projects(Project_ID)
        ON DELETE CASCADE
);

-- Sensor_Data table
CREATE TABLE IF NOT EXISTS Sensor_Data (
    Data_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    Sensor_ID INT NOT NULL,
    Timestamp TIMESTAMP NOT NULL,
    Value FLOAT NOT NULL,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
        ON DELETE CASCADE,
    INDEX idx_sensor_time (Sensor_ID, Timestamp)
);

-- Power_Generation table
CREATE TABLE IF NOT EXISTS Power_Generation (
    Generation_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    Project_ID INT NOT NULL,
    Timestamp TIMESTAMP NOT NULL,
    Power_Generated FLOAT NOT NULL,
    Aggregation_Interval ENUM('30s', '5min', 'hourly', 'daily') DEFAULT 'hourly',
    Derived_From_Sensor INT,
    FOREIGN KEY (Project_ID) REFERENCES Projects(Project_ID),
    FOREIGN KEY (Derived_From_Sensor) REFERENCES Sensors(Sensor_ID)
);
"""

# ---------------------------
# Database Initializer
# ---------------------------
def create_mysql_schema():
    """Connect to MySQL and create tables if they don't exist."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        logging.info(f"Connected to DB: {cursor.fetchone()[0]}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        for stmt in SCHEMA_SQL.strip().split(";"):
            if stmt.strip():
                cursor.execute(stmt + ";")
        conn.commit()
        logging.info("Schema created successfully.")
    except Exception as e:
        logging.error(f"Schema creation failed: {e}")
    finally:
        if conn:
            conn.close()

# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    create_mysql_schema()
