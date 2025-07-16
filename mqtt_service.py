import json
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from dateutil import parser
from database import SessionLocal, Device, DeviceStatusHistory

MQTT_BROKER = "iot.salieabs.in"
MQTT_PORT = 1883
MQTT_TOPIC = "GS2526002_OUT"

# Track last insert time per device
last_written = {}

def on_connect(client, userdata, flags, rc):
    print("✅ Connected with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("device_uid")
        status = payload.get("Status")
        timestamp_str = payload.get("timestamp")

        if not device_id or status is None or not timestamp_str:
            return

        try:
            if "Z+" in timestamp_str or "Z-" in timestamp_str:
                timestamp_str = timestamp_str.replace("Z", "")
            elif timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str.replace("Z", "+00:00")

            last_ping = parser.isoparse(timestamp_str)
        except Exception as e:
            print(f"❌ Invalid timestamp format: {timestamp_str}", e)
            return

        online = status == "1"

        db = SessionLocal()

        # Update current device table
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if device:
            device.last_ping = last_ping
            device.online = online
        else:
            device = Device(device_id=device_id, last_ping=last_ping, online=online)
            db.add(device)

        # Save to history if last record > 1 min ago
        last_time = last_written.get(device_id)
        if not last_time or (last_ping - last_time).total_seconds() >= 60:
            history = DeviceStatusHistory(
                device_id=device_id,
                online=online,
                timestamp=last_ping
            )
            db.add(history)
            last_written[device_id] = last_ping

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

if __name__ == "__main__":
    start_mqtt()
    while True:
        pass