from typing import List, Optional
from pydantic import BaseModel

from py_ocpi.core.data_types import CiString, URL, DisplayText, DateTime
from py_ocpi.modules.commands.v_2_2_1.enums import CommandResponseType, CommandResultType
from py_ocpi.modules.tokens.v_2_2_1.schemas import Token


class CancelReservation(BaseModel):
    response_url: URL
    reservation_id: CiString(36)


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
    reservation_id: CiString(36)
    location_id: CiString(36)
    evse_uid: Optional[CiString(36)]
    authorization_reference: Optional[CiString(36)]


class StartSession(BaseModel):
    response_url: URL
    token: Token
    location_id: CiString(36)
    evse_uid: Optional[CiString(36)]
    connector_id: Optional[CiString(36)]
    authorization_reference: Optional[CiString(36)]


class StopSession(BaseModel):
    response_url: URL
    session_id: CiString(36)


class UnlockConnector(BaseModel):
    response_url: URL
    location_id: CiString(36)
    evse_uid: CiString(36)
    connector_id: CiString(36)
