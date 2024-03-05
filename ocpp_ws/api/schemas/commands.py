from datetime import datetime, timezone
from typing import List, Optional, Union

from py_ocpi.modules.commands.v_2_2_1.enums import CommandResponseType, CommandResultType
from pydantic import BaseModel

from py_ocpi.core.data_types import CiString, URL, DateTime, DisplayText

from py_ocpi.modules.tokens.v_2_2_1.schemas import Token




class CancelReservation(BaseModel):
    response_url: URL
    reservation_id: str


class CommandResponse(BaseModel):
    result: CommandResponseType
    timeout: int
    message: List[DisplayText] = []


class CommandResult(BaseModel):
    result: CommandResultType
    message: List[DisplayText] = []


class ReserveNow(BaseModel):
    response_url: URL
    token: Token
    expiry_date: DateTime
    reservation_id: str
    location_id: str
    evse_uid: str
    authorization_reference: str


class StartSession(BaseModel):
    response_url: str
    token: Token
    location_id: str
    evse_uid: Optional[str]
    connector_id: Optional[str]
    authorization_reference: Optional[str]


class StopSession(BaseModel):
    response_url: URL
    session_id: CiString(36)


class UnlockConnector(BaseModel):
    response_url: URL
    location_id: CiString(36)
    evse_uid: CiString(36)
    connector_id: CiString(36)
