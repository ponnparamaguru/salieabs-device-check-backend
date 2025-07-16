import json
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from database import SessionLocal, Device, DeviceStatusHistory

MQTT_BROKER = "iot.salieabs.in"
MQTT_PORT = 1883
MQTT_TOPIC = "GS2526002_OUT"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(MQTT_TOPIC)

last_written = {}

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("device_uid")
        status = payload.get("Status")

        if not device_id or status is None:
            return

        online = status == "1"
        now = datetime.utcnow()

        # Only insert into history if 60 seconds have passed
        last_time = last_written.get(device_id)
        if not last_time or (now - last_time) >= timedelta(minutes=1):
            db = SessionLocal()
            # Save status to history
            history = DeviceStatusHistory(
                device_id=device_id,
                online=online,
                timestamp=now
            )
            db.add(history)

            # Also update current status
            device = db.query(Device).filter(Device.device_id == device_id).first()
            if device:
                device.last_ping = now
                device.online = online
            else:
                device = Device(device_id=device_id, last_ping=now, online=online)
                db.add(device)

            db.commit()
            db.close()

            last_written[device_id] = now

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