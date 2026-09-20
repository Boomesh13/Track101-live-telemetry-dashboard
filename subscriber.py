import time
import paho.mqtt.client as mqtt
 
BROKER = "localhost"
PORT = 1883
TRUCK_ID = "truck101"
 
TOPIC_STATUS = f"fleet/{TRUCK_ID}/status"
TOPIC_ENGINE_TEMP = f"fleet/{TRUCK_ID}/engine/temp"
TOPIC_GPS = f"fleet/{TRUCK_ID}/gps/location"
TOPIC_FUEL = f"fleet/{TRUCK_ID}/fuel/level"
# Note: TOPIC_SPEED is deliberately NOT subscribed to here.
 
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[dashboard] Connected to broker.")
        client.subscribe(TOPIC_STATUS, qos=1)
        client.subscribe(TOPIC_ENGINE_TEMP, qos=1)
        client.subscribe(TOPIC_GPS, qos=1)
        client.subscribe(TOPIC_FUEL, qos=1)
        print("[dashboard] Subscribed to: status, engine/temp, gps/location, fuel/level")
        print("[dashboard] (speed is intentionally excluded)")
    else:
        print(f"[dashboard] Connection failed with code {rc}")
 
 
def on_message(client, userdata, msg):
    timestamp = time.strftime("%H:%M:%S")
    payload = msg.payload.decode()
    print(f"[{timestamp}] {msg.topic} -> {payload}")
 
 
client = mqtt.Client(client_id="fleet-dashboard")
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(BROKER, PORT, keepalive=30)
 
print("[dashboard] Listening (no speed)... Press Ctrl+C to stop.")
client.loop_forever()