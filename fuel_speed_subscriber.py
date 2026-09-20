import time
import paho.mqtt.client as mqtt
 
BROKER = "localhost"
PORT = 1883
TRUCK_ID = "truck101"
 
# Subscribe to exactly these two topics only -- nothing else.
TOPIC_FUEL = f"fleet/{TRUCK_ID}/fuel/level"
TOPIC_SPEED = f"fleet/{TRUCK_ID}/speed"
 
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[fuel-speed-monitor] Connected to broker.")
        client.subscribe(TOPIC_FUEL, qos=1)
        client.subscribe(TOPIC_SPEED, qos=1)
        print(f"[fuel-speed-monitor] Subscribed to:\n  {TOPIC_FUEL}\n  {TOPIC_SPEED}")
    else:
        print(f"[fuel-speed-monitor] Connection failed with code {rc}")
 
 
def on_message(client, userdata, msg):
    timestamp = time.strftime("%H:%M:%S")
    payload = msg.payload.decode()
 
    if msg.topic == TOPIC_FUEL:
        print(f"[{timestamp}] Fuel level  -> {payload}%")
    elif msg.topic == TOPIC_SPEED:
        print(f"[{timestamp}] Speed       -> {payload} km/h")
 
 
client = mqtt.Client(client_id="fuel-speed-monitor")
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(BROKER, PORT, keepalive=30)
 
print("[fuel-speed-monitor] Listening for fuel & speed only... Press Ctrl+C to stop.")
client.loop_forever()