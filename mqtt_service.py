import json
import paho.mqtt.client as mqtt
from datetime import datetime
from database import SessionLocal, Device

MQTT_BROKER = "iot.salieabs.in"
MQTT_PORT = 1883
MQTT_TOPIC = "GS2526002_OUT"

def on_connect(client, userdata, flags, rc):
    print("✅ Connected with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("device_uid")
        status = payload.get("Status")
        timestamp = payload.get("timestamp")

        if not device_id or status is None or not timestamp:
            return

        # Parse online status from Status string
        online = status == "1"
        last_ping = datetime.now()  # Optional: parse `timestamp` for accuracy

        db = SessionLocal()
        device = db.query(Device).filter(Device.device_id == device_id).first()

        if device:
            device.last_ping = last_ping
            device.online = online
        else:
            device = Device(device_id=device_id, last_ping=last_ping, online=online)
            db.add(device)

        db.commit()
        db.close()

        print(f"📡 {device_id} → {'ON' if online else 'OFF'} @ {last_ping}")

    except Exception as e:
        print("❌ Error handling message:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()