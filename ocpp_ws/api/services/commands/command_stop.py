from ocpp.v16.enums import RemoteStartStopStatus
from py_ocpi.modules.commands.v_2_2_1.enums import CommandResultType
from sqlalchemy import select

from ocpp_ws.api.models.locations import ChargePoint as ChargePointModel
from ocpp_ws.api.schemas.commands import CommandResult
from ocpp_ws.app.dependencies import ACTIVE_CONNECTIONS, async_session
from ocpp_ws.charge_point_v1_6 import ChargePoint


async def stop_session(session_id: str) -> CommandResult:
    # async with async_session() as session:
    #     result = await session.execute(
    #         select(ChargePointModel).where(
    #             ChargePointModel.location_id == int(location_id),
    #             ChargePointModel.id == int(evse_uid)
    #         )
    #     )
    #     charge_point = result.scalars().first()
    #
    # if not charge_point:
    #     return CommandResult(result=CommandResultType.rejected)
    #
    # if charge_point.identity not in ACTIVE_CONNECTIONS:
    #     return CommandResult(result=CommandResultType.rejected)

    active_charge_point: ChargePoint = ACTIVE_CONNECTIONS.get('identity-001')

    # todo generate ID_TAG

    response = await active_charge_point.send_remote_stop_transaction_command(transaction_id=int(session_id))

    return CommandResult(result={
        RemoteStartStopStatus.accepted: CommandResultType.accepted,
        RemoteStartStopStatus.rejected: CommandResultType.rejected
    }.get(response.status))
