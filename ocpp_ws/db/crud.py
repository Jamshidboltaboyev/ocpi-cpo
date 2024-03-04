from datetime import datetime

from ocpp_ws.db.models import ChargePoint
from sqlalchemy.future import select
from sqlalchemy import update

from ocpp_ws.db.session import async_session


async def get_charge_point(charge_point_identify):
    async with async_session() as session:
        result = await session.execute(
            select(ChargePoint).where(ChargePoint.identity == charge_point_identify)
        )
        charge_point = result.scalars().first()
        return charge_point


async def update_charge_point_on_boot_notification(charge_point_identity):
    async with async_session() as session:
        current_time = datetime.utcnow()
        async with session.begin():
            return await session.execute(
                update(ChargePoint).
                where(ChargePoint.identity == charge_point_identity).
                values(last_heartbeat=current_time, is_connected=True)
            )


async def update_charge_point_on_disconnect(charge_point_identity):
    async with async_session() as session:
        current_time = datetime.utcnow()
        async with session.begin():
            return await session.execute(
                update(ChargePoint).
                where(ChargePoint.identity == charge_point_identity).
                values(last_heartbeat=current_time, is_connected=False)
            )


async def update_charge_point_on_connect(charge_point_identity):
    async with async_session() as session:
        async with session.begin():
            return await session.execute(
                update(ChargePoint).
                where(ChargePoint.identity == charge_point_identity).
                values(is_connected=True)
            )


async def update_charge_point_on_heartbeat(charge_point_identity):
    pass
