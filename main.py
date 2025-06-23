from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, Device
from mqtt_service import start_mqtt

app = FastAPI()

# ✅ Allow ALL origins for development/testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Allow all origins (only for dev!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start MQTT listener
start_mqtt()

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
