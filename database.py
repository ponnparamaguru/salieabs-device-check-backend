from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./db.sqlite3"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True, index=True)
    last_ping = Column(DateTime, default=datetime.utcnow)
    online = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

class DeviceStatusHistory(Base):
    __tablename__ = "device_status_history"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    online = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
