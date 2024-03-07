import enum

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Session(Base):
    __tablename__ = 'session'

    class AuthMethod(enum.Enum):
        AUTH_REQUEST = "AUTH_REQUEST"
        COMMAND = "COMMAND"
        WHITELIST = "WHITELIST"

    id = Column(Integer, primary_key=True)
    country_code = Column(String(2))
    party_id = Column(String(3))
    start_date_time = Column(DateTime)
    end_date_time = Column(DateTime, nullable=True)
    kwh = Column(Float)
    cdr_token_id = Column(Integer, ForeignKey('cdr_token.id'), nullable=False)
    # cdr_token = relationship('CdrToken', back_populates='sessions')
    auth_method = Column(Enum(AuthMethod))
    authorization_reference = Column(String(36), nullable=True)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    # location = relationship('Location', back_populates='sessions')
    evse_id = Column(Integer, ForeignKey('charge_point.id'), nullable=False)
    # evse = relationship('ChargePoint', back_populates='sessions')
    connector_id = Column(String(36))
    meter_id = Column(String(255), nullable=True)
    currency = Column(String(3))
    charging_periods = Column(JSON, default=list)
    total_cost = Column(Float, nullable=True)
    status = Column(String(30))
