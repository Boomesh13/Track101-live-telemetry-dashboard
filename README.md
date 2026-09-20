🚚 Truck101 Live Telemetry Dashboard

A real-time IoT telemetry pipeline that simulates a truck sending live sensor data over MQTT, stores it in PostgreSQL, and visualizes it on a live-updating Streamlit dashboard.

📊 Architecture
publisher.py (simulated truck sensor)
    → MQTT Broker (Mosquitto)
        → mqtt_to_db.py (subscriber, saves to DB)
            → PostgreSQL (truck_readings table)
                → dashboard.py (Streamlit live dashboard)
🔧 What it does
publisher.py — simulates a truck (truck101) publishing engine temperature, GPS location, fuel level, and speed every 3 seconds over MQTT.
Uses QoS 1 for reliable delivery, a Last Will and Testament (LWT) message so the system knows if the truck goes offline unexpectedly, and retained messages so new subscribers instantly get the last known GPS location.
subscriber.py — a general dashboard subscriber that listens to status, engine temp, GPS, and fuel.
fuel_speed_subscriber.py — a focused subscriber that listens only to fuel and speed, demonstrating how MQTT topics let different clients subscribe to just the data they need.
mqtt_to_db.py — subscribes to all telemetry topics and writes each reading into a PostgreSQL table in real time.
dashboard.py — a Streamlit web dashboard that queries PostgreSQL and displays live metrics, interactive charts (Plotly), and the truck's last known location on a map. Auto-refreshes every 3 seconds.
🖼️ Dashboard Preview

Show Image Show Image
<img width="1870" height="742" alt="Screenshot 2026-09-20 202813" src="https://github.com/user-attachments/assets/42b918eb-9172-4907-9417-1f5a61eea8df" />
<img width="1875" height="632" alt="Screenshot 2026-09-20 203353" src="https://github.com/user-attachments/assets/40d57135-64c4-42c2-aea4-700ad406817d" />

🛠️ Tech Stack
Python
MQTT (Eclipse Mosquitto broker + paho-mqtt client library)
PostgreSQL (psycopg2)
Streamlit + Plotly (dashboard/visualization)
▶️ How to run it locally
Install and start a local Mosquitto broker
Create a PostgreSQL database truck_telemetry and run create_table.sql
Create a .env file with your database password:
   DB_PASSWORD=your_password_here
Install dependencies:
   pip install paho-mqtt psycopg2-binary streamlit plotly streamlit-autorefresh python-dotenv pandas
Run each in its own terminal:
   python publisher.py
   python mqtt_to_db.py
   streamlit run dashboard.py
💡 Why this project

Built to demonstrate hands-on understanding of MQTT (topics, QoS levels, Last Will, retained messages) applied to a realistic IoT/fleet-telematics use case — publishing sensor data, persisting it, and visualizing it live end to end.
