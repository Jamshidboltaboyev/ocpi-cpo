import enum

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CdrToken(Base):
    __tablename__ = 'cdr_token'

    class TokenType(enum.Enum):
        AD_HOC_USER = 'AD_HOC_USER'
        APP_USER = 'APP_USER'
        OTHER = 'OTHER'
        RFID = 'RFID'

    id = Column(Integer, primary_key=True)
    country_code = Column(String(2))
    party_id = Column(String(3))
    uid = Column(String(36))
    type = Column(Enum(TokenType))
    contract_id = Column(String(36))

    # sessions = relationship('Session', back_populates='cdr_token')

    def __repr__(self):
        return f"{self.uid} - {self.type}"
