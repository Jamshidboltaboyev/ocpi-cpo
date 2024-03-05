from __future__ import annotations

from datetime import datetime

from ocpp.routing import on
from ocpp.v16 import ChargePoint as ChargePoint_V_1_6
from ocpp.v16 import call
from ocpp.v16.enums import *
from sqlalchemy import update

from ocpp_ws.api.models.locations import ChargePoint as ChargePointModel
from ocpp_ws.app.dependencies import async_session


class ChargePoint(ChargePoint_V_1_6):

    async def route_message(self, raw_msg):
        # await send_msg_cp_log(f"{self.id}\n{raw_msg}")
        return await super().route_message(raw_msg)

    @on(action=Action.BootNotification)
    async def on_boot_notification(self, **kwargs):
        async with async_session() as session:
            current_time = datetime.utcnow()
            async with session.begin():
                await session.execute(
                    update(ChargePoint).
                    where(ChargePointModel.identity == self.id).
                    values(last_heartbeat=current_time, is_connected=True)
                )

        return self._call_result.BootNotificationPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+05:00'),
            interval=10, status=RegistrationStatus.accepted
        )

    @on(action=Action.Heartbeat)
    async def on_heartbeat(self, **kwargs):
        async with async_session() as session:
            current_time = datetime.now()
            async with session.begin():
                await session.execute(
                    update(ChargePointModel).where(ChargePointModel.identity == self.id).
                    values(last_heartbeat=current_time)
                )
        return self._call_result.HeartbeatPayload(current_time=datetime.utcnow().isoformat())

    async def send_remote_start_transaction_command(self, connector_id: int, id_tag: str):
        payload = call.RemoteStartTransactionPayload(connector_id=connector_id, id_tag=str(id_tag))
        return await self.call(payload=payload)

    async def send_remote_stop_transaction_command(self, transaction_id: int):
        payload = call.RemoteStopTransactionPayload(transaction_id=transaction_id)
        return await self.call(payload=payload)
