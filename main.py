from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine, Device, DeviceStatusHistory
from mqtt_service import start_mqtt
from datetime import datetime, time, timedelta
from typing import List

Base.metadata.create_all(bind=engine)
app = FastAPI()
# Start MQTT listener
start_mqtt()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/devices")
def get_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()

@app.get("/devices/{device_id}")
def get_device(device_id: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if device:
        return device
    return {"error": "Device not found"}

@app.get("/devices/{device_id}/status-history")
def get_device_history(
    device_id: str,
    start: datetime = Query(default_factory=lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)),
    end: datetime = Query(default_factory=lambda: datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)),
    db: Session = Depends(get_db)
):
    data = db.query(DeviceStatusHistory).filter(
        DeviceStatusHistory.device_id == device_id,
        DeviceStatusHistory.timestamp >= start,
        DeviceStatusHistory.timestamp <= end
    ).order_by(DeviceStatusHistory.timestamp).all()

    return [
        {
            "timestamp": d.timestamp.isoformat(),
            "online": d.online
        } for d in data
    ]