from __future__ import annotations

from datetime import datetime

from ocpp.routing import on
from ocpp.v16 import ChargePoint as ChargePoint_V_1_6
from ocpp.v16 import call
from ocpp.v16.enums import *
from sqlalchemy import update
from sqlalchemy.engine import CursorResult

from ocpp_ws.db.models import ChargePoint as ChargePointModel
from ocpp_ws.db.crud import (
    update_charge_point_on_boot_notification
)
from ocpp_ws.db.session import async_session
from ocpp_ws.utils import send_msg_cp_log


class ChargePoint(ChargePoint_V_1_6):

    async def route_message(self, raw_msg):
        await send_msg_cp_log(f"{self.id}\n{raw_msg}")
        return await super().route_message(raw_msg)

    @on(action=Action.BootNotification)
    async def on_boot_notification(self, **kwargs):

        await update_charge_point_on_boot_notification(self.id)

        return self._call_result.BootNotificationPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+05:00'),
            interval=10, status=RegistrationStatus.accepted
        )

    @on(action=Action.Heartbeat)
    async def on_heartbeat(self, **kwargs):
        async with async_session() as session:
            current_time = datetime.now()
            async with session.begin():
                result: CursorResult = await session.execute(
                    update(ChargePointModel).where(ChargePointModel.identity == self.id).
                    values(last_heartbeat=current_time)
                )
                print(result.rowcount)
        return self._call_result.HeartbeatPayload(current_time=datetime.utcnow().isoformat())

    async def send_remote_start_transaction_command(self, connector_id: int, id_tag: str):
        payload = call.RemoteStartTransactionPayload(connector_id=int(connector_id), id_tag=str(id_tag))
        await self.call(payload=payload)

    async def send_remote_stop_transaction_command(self, transaction_id: int):
        payload = call.RemoteStopTransactionPayload(transaction_id=int(transaction_id))
        await self.call(payload=payload)
