import time
import json
import psycopg2
import paho.mqtt.client as mqtt
 
# --- MQTT settings ---
BROKER = "localhost"
PORT = 1883
TRUCK_ID = "truck101"
 
TOPIC_ENGINE_TEMP = f"fleet/{TRUCK_ID}/engine/temp"
TOPIC_GPS = f"fleet/{TRUCK_ID}/gps/location"
TOPIC_FUEL = f"fleet/{TRUCK_ID}/fuel/level"
TOPIC_SPEED = f"fleet/{TRUCK_ID}/speed"
 
# --- PostgreSQL settings ---
# Update these if your setup differs.
DB_CONFIG = {
    "dbname": "truck_telemetry",
    "user": "postgres",
    "password": "boomesh1329",
    "host": "localhost",
    "port": "5432",
}
 
# We keep the latest values in memory and write a combined row
# whenever a new reading comes in, so each row has all fields filled.
latest = {"engine_temp": None, "fuel_level": None, "speed": None,
          "latitude": None, "longitude": None}
 
 
def get_connection():
    return psycopg2.connect(**DB_CONFIG)
 
 
def insert_reading(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO truck_readings
                (truck_id, engine_temp, fuel_level, speed, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                TRUCK_ID,
                latest["engine_temp"],
                latest["fuel_level"],
                latest["speed"],
                latest["latitude"],
                latest["longitude"],
            ),
        )
    conn.commit()
 
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[db-writer] Connected to MQTT broker.")
        client.subscribe(TOPIC_ENGINE_TEMP, qos=1)
        client.subscribe(TOPIC_GPS, qos=1)
        client.subscribe(TOPIC_FUEL, qos=1)
        client.subscribe(TOPIC_SPEED, qos=1)
        print("[db-writer] Subscribed to engine/temp, gps/location, fuel/level, speed")
    else:
        print(f"[db-writer] MQTT connection failed with code {rc}")
 
 
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
 
    if msg.topic == TOPIC_ENGINE_TEMP:
        latest["engine_temp"] = float(payload)
    elif msg.topic == TOPIC_FUEL:
        latest["fuel_level"] = float(payload)
    elif msg.topic == TOPIC_SPEED:
        latest["speed"] = float(payload)
    elif msg.topic == TOPIC_GPS:
        gps = json.loads(payload)
        latest["latitude"] = gps["lat"]
        latest["longitude"] = gps["lon"]
 
    try:
        insert_reading(userdata["conn"])
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Saved -> temp={latest['engine_temp']} "
              f"fuel={latest['fuel_level']} speed={latest['speed']} "
              f"lat={latest['latitude']} lon={latest['longitude']}")
    except Exception as e:
        # Roll back the failed transaction so the connection can be used
        # again for the next insert -- without this, every insert after
        # the first failure also fails with "transaction is aborted".
        userdata["conn"].rollback()
        print(f"[db-writer] DB insert failed: {e}")
 
 
conn = get_connection()
print("[db-writer] Connected to PostgreSQL.")
 
client = mqtt.Client(client_id="db-writer", userdata={"conn": conn})
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(BROKER, PORT, keepalive=30)
 
print("[db-writer] Listening and saving to DB... Press Ctrl+C to stop.")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[db-writer] Shutting down...")
    conn.close()