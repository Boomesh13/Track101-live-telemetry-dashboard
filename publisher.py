import time
import random
import json
import paho.mqtt.client as mqtt
 
BROKER = "localhost"
PORT = 1883
TRUCK_ID = "truck101"
 
TOPIC_STATUS = f"fleet/{TRUCK_ID}/status"
TOPIC_ENGINE_TEMP = f"fleet/{TRUCK_ID}/engine/temp"
TOPIC_GPS = f"fleet/{TRUCK_ID}/gps/location"
TOPIC_FUEL = f"fleet/{TRUCK_ID}/fuel/level"
TOPIC_SPEED = f"fleet/{TRUCK_ID}/speed"
 
client = mqtt.Client(client_id=f"{TRUCK_ID}-publisher")
 
# --- Last Will and Testament ---
# If this client disconnects unexpectedly, the broker publishes this
# on our behalf so subscribers know the truck went offline.
client.will_set(TOPIC_STATUS, payload="offline", qos=1, retain=True)
 
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[{TRUCK_ID}] Connected to broker.")
        client.publish(TOPIC_STATUS, payload="online", qos=1, retain=True)
    else:
        print(f"[{TRUCK_ID}] Connection failed with code {rc}")
 
 
client.on_connect = on_connect
client.connect(BROKER, PORT, keepalive=30)
client.loop_start()
 
lat, lon = 12.9716, 77.5946
fuel = 80.0
speed = 60.0  # km/h, starting speed
 
try:
    while True:
        # --- Engine temperature ---
        engine_temp = round(random.uniform(85, 105), 1)
        client.publish(TOPIC_ENGINE_TEMP, payload=engine_temp, qos=1)
 
        # --- GPS location (drifts slightly each cycle) ---
        lat += random.uniform(-0.001, 0.001)
        lon += random.uniform(-0.001, 0.001)
        gps_payload = json.dumps({"lat": round(lat, 5), "lon": round(lon, 5)})
        client.publish(TOPIC_GPS, payload=gps_payload, qos=1, retain=True)
 
        # --- Fuel level (slowly decreases) ---
        fuel = max(0, fuel - random.uniform(0.1, 0.5))
        client.publish(TOPIC_FUEL, payload=round(fuel, 1), qos=1)
 
        # --- Speed (fluctuates realistically, e.g. highway driving) ---
        speed += random.uniform(-5, 5)
        speed = max(0, min(speed, 100))  # keep between 0 and 100 km/h
        client.publish(TOPIC_SPEED, payload=round(speed, 1), qos=1)
 
        print(f"[{TRUCK_ID}] temp={engine_temp}C  gps={gps_payload}  "
              f"fuel={round(fuel,1)}%  speed={round(speed,1)}km/h")
        time.sleep(3)
 
except KeyboardInterrupt:
    print(f"\n[{TRUCK_ID}] Shutting down cleanly...")
    client.publish(TOPIC_STATUS, payload="offline", qos=1, retain=True)
    client.loop_stop()
    client.disconnect()