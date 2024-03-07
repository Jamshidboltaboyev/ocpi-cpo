from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()


class Location(Base):
    __tablename__ = 'locations_location'

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    district_id = Column(Integer, ForeignKey('district.id'))
    id = Column(Integer, primary_key=True)

    # sessions = relationship('Session', back_populates='location')
    # charge_point = relationship("ChargePoint", back_populates='location')


class ChargePoint(Base):
    __tablename__ = 'locations_chargepoint'

    class Status(enum.Enum):
        AVAILABLE = 'AVAILABLE'
        BLOCKED = "BLOCKED"
        CHARGING = 'CHARGING'
        INOPERATIVE = 'INOPERATIVE'
        OUTOFORDER = "OUTOFORDER"
        PLANNED = "PLANNED"
        REMOVED = "REMOVED"
        RESERVED = "RESERVED"
        UNKNOWN = "UNKNOWN"

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('location.id'))
    identity = Column(String(50), )
    boot_timestamp = Column(DateTime, nullable=True)
    model = Column(String(128), nullable=True)
    vendor = Column(String(128), nullable=True)
    serial_number = Column(String(25), nullable=True)
    firmware = Column(String(50), nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)
    is_connected = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    status = Column(Enum(Status))

    # sessions = relationship('Session', back_populates='evse')
