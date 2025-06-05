Energy Monitoring System
A modular Python-based IoT data pipeline for simulating and collecting sensor data from renewable energy microgeneration projects (solar and wind), with aggregation, local database storage, and cloud dashboard integration via ThingSpeak.

🚀 Project Overview
This project simulates and monitors three renewable energy test systems:

🔆 Solar Facade

🧱 Solar Brick

🌬️ Horizontal Axis Wind Turbine (HAWT)

Each system simulates sensors that generate data every 30 seconds, stored as CSVs, aggregated into Parquet files every 30 minutes, and uploaded to:
- A local MySQL database
- ThingSpeak channels for real-time cloud monitoring
- Power BI dashboards will later consume both cloud and SQL data for analysis and visualization.

📁 Folder Structure

energy_monitoring/
├── config/
│   └── sensor_config.json        # Sensor metadata & field mapping
├── data/
│   ├── raw/                      # CSVs by day, 30s interval
│   └── processed/                # Hourly Parquet files
├── db/
│   └── (Optional SQLite.db)      # Use MySQL in deployment
├── logs/
│   └── *.log                     # Runtime logs per task
├── scripts/
│   ├── cron_manager.py           # Master scheduler
│   ├── generate_sample_data.py   # Simulates data every 30s
│   ├── aggregate_parquet.py      # Aggregates CSV → Parquet every 30min
│   ├── upload_to_sql.py          # Uploads Parquet to MySQL
│   └── upload_thingspeak.py      # Pushes values to ThingSpeak
├── requirements.txt
└── README.md


⚙️ Setup Instructions
1. Clone and install dependencies
'''bash
pip install -r requirements.txt
'''
2. Set up MySQL database
Log into MySQL and run:

'''sql
CREATE DATABASE energy_monitoring;
USE energy_monitoring;

-- Paste schema from /docs or provided schema.sql
'''
Configure DB credentials in scripts/upload_to_sql.py and 'upload_thingspeak.py' under 'DB_CONFIG'.

3. Configure sensor channels
- Update config/sensor_config.json:
    - List all sensor_id, type, unit, project_id, and field number (ThingSpeak)
- Make sure each sensor exists in the Sensors table of your DB
- Create channels in ThingSpeak, note their write API keys, and add them to upload_thingspeak.py.

🛠 How to Run
To run the full pipeline (Windows or Raspberry Pi):

'''bash
python scripts/cron_manager.py
'''
It will schedule and run:
- Data simulation every 30s
- Aggregation every 30min
- Upload to SQL every 30min
- Upload to ThingSpeak every 10min

—

✅ Test Run:

To test scripts individually:

'''bash
python scripts/generate_sample_data.py
python scripts/aggregate_parquet.py
python scripts/upload_to_sql.py
python scripts/upload_thingspeak.py
'''
📡 ThingSpeak Setup
- 1 channel per project
- Map sensors → fields (field1 to field8)
- Write API key is used per project in upload_thingspeak.py
- See: https://thingspeak.com/