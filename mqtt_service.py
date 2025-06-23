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
        timestamp = payload.get("timestamp")

        if not device_id or not timestamp:
            return

        last_ping = datetime.now()  # You could parse timestamp if it's reliable

        db = SessionLocal()
        device = db.query(Device).filter(Device.device_id == device_id).first()

        if device:
            device.last_ping = last_ping
            device.online = True
        else:
            device = Device(device_id=device_id, last_ping=last_ping, online=True)
            db.add(device)

        db.commit()
        db.close()

    except Exception as e:
        print("❌ Error handling message:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()