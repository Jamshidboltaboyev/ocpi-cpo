from datetime import datetime
from typing import Tuple, Union

from ocpp.v16.enums import RemoteStartStopStatus
from py_ocpi.modules.commands.v_2_2_1.enums import CommandResultType
from sqlalchemy import select

from ocpp_ws.api.models.cdrs import CdrToken
from ocpp_ws.api.models.locations import ChargePoint as ChargePointModel
from ocpp_ws.api.models.sessions import Session
from ocpp_ws.api.schemas.commands import CommandResult, StartSession
from ocpp_ws.app.config import PARTY_ID, COUNTRY_CODE
from ocpp_ws.app.dependencies import ACTIVE_CONNECTIONS, async_session
from ocpp_ws.charge_point_v1_6 import ChargePoint


async def start_session(start_session_data: StartSession) -> CommandResult:
    has_error, result = await validate_charge_point(start_session_data.location_id, start_session_data.evse_uid)
    if has_error:
        return result

    session: int = await create_session(data=start_session_data)

    active_charge_point: ChargePoint = ACTIVE_CONNECTIONS[result.identity]
    response = await active_charge_point.send_remote_start_transaction_command(
        connector_id=int(start_session_data.connector_id), id_tag=str(session.id)
    )

    return CommandResult(result={
        RemoteStartStopStatus.accepted: CommandResultType.accepted,
        RemoteStartStopStatus.rejected: CommandResultType.rejected
    }.get(response.status))


async def validate_charge_point(location_id, evse_uid) -> Tuple[bool, Union[CommandResult, ChargePointModel]]:
    async with async_session() as session:
        result = await session.execute(
            select(ChargePointModel).where(
                ChargePointModel.location_id == int(location_id),
                ChargePointModel.id == int(evse_uid)
            )
        )
        charge_point = result.scalars().first()

    if not charge_point:
        return True, CommandResult(result=CommandResultType.rejected)

    if charge_point.identity not in ACTIVE_CONNECTIONS:
        return True, CommandResult(result=CommandResultType.rejected)

    return False, charge_point


async def create_session(data: StartSession):
    cdr_token = CdrToken(
        country_code=COUNTRY_CODE,
        party_id=PARTY_ID,
        uid=data.token.uid,
        type=data.token.type,
        contract_id=data.token.contract_id
    )

    async with async_session() as db_session:
        db_session.add(cdr_token)
        db_session.commit()
        db_session.refresh(cdr_token)

    session = Session(
        country_code=COUNTRY_CODE,
        party_id=PARTY_ID,
        start_date_time=datetime.now(),
        # end_date_time=None,
        kwh=0,
        cdr_token_id=cdr_token.id,
        auth_method=Session.AuthMethod.AUTH_REQUEST,
        authorization_reference=data.authorization_reference,
        location_id=int(data.location_id),
        evse_id=int(data.evse_uid),
        connector_id=data.connector_id,
        meter_id='0',
        currency='USD',
        charging_periods=[{'start': '2024-03-06T12:00:00', 'end': '2024-03-06T14:00:00'}],
        status='ACTIVE'
    )

    async with async_session() as db_session:
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

    return session.id
