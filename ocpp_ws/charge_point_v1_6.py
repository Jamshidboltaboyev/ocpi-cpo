from __future__ import annotations

from datetime import datetime

import aiohttp
from channels.db import database_sync_to_async
from django.utils import timezone
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.datatypes import IdTagInfo
from ocpp.v16.enums import *

from accounts.models import CustomUser
from core import models
from core.models import UserBalanceHistory


async def send_msg_cp_log(message):
    token = '6758742667:AAGWYLcppQAlSbhjGZS16QdpSb5lIgM1sT0'
    channel_id = -1002034772310
    user_id = 1260770782
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': channel_id,
        'text': message
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            await response.json()


class ChargePoint(cp):

    async def route_message(self, raw_msg):
        await send_msg_cp_log(f"{self.id}\n{raw_msg}")
        return await super().route_message(raw_msg)

    @on(action=Action.BootNotification)
    async def on_boot_notification(self, **kwargs):
        charge_point = await models.ChargePoint.objects.filter(identity=self.id).afirst()

        if not charge_point:
            return self._call_result.BootNotificationPayload(
                current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+05:00'),
                interval=10, status=RegistrationStatus.rejected
            )

        charge_point.connected = True
        charge_point.last_heartbeat = timezone.now()
        await charge_point.asave(update_fields=['connected', 'last_heartbeat'])

        return self._call_result.BootNotificationPayload(
            current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+05:00'),
            interval=10, status=RegistrationStatus.accepted
        )

    @on(action=Action.Heartbeat)
    async def on_heartbeat(self, **kwargs):
        charge_point = await models.ChargePoint.objects.filter(identity=self.id).afirst()

        charge_point.last_heartbeat = timezone.now()
        await charge_point.asave(update_fields=['last_heartbeat'])

        return self._call_result.HeartbeatPayload(current_time=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+05:00'))

    @on(action=Action.MeterValues)
    async def on_meter_values(self, transaction_id, meter_value, **kwargs):
        ipt = await models.InProgressTransaction.objects.filter(pk=transaction_id).afirst()

        measurand_mapping = {
            'Current.Import': 'current',
            'Energy.Active.Import.Register': 'energy',
            'Power.Active.Import': 'power',
            'SoC': 'soc',
            'Voltage': 'voltage',
        }

        for meter_value_item in meter_value:
            meter_value_item = meter_value_item['sampled_value'][0]
            measurand = meter_value_item.get('measurand', None)
            value = float(meter_value_item.get('value', 0))
            if measurand in measurand_mapping:
                setattr(ipt, measurand_mapping[measurand], value)
        await ipt.asave()

        return self._call_result.MeterValuesPayload()

    @on(action=Action.StatusNotification)
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        connector = await models.Connector.objects.filter(charge_point__identity=self.id,
                                                          connector_id=connector_id).afirst()
        if not connector:
            return self._call_result.StatusNotificationPayload()  # TODO refactor

        status_mapping = {
            'Available': {'available': True, 'in_use': False},
            'Charging': {'available': True, 'in_use': True},
            'Preparing': {'available': False, 'in_use': False},
        }
        if status in status_mapping:
            connector.available = status_mapping[status]['available']
            connector.in_use = status_mapping[status]['in_use']
            connector.status = status

        await connector.asave()
        return self._call_result.StatusNotificationPayload()

    @on(Action.StartTransaction)
    async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        connector = await models.Connector.objects.filter(connector_id=connector_id,
                                                          charge_point__identity=self.id).afirst()
        chpt = await models.ChargePointTask.objects.filter(pk=int(id_tag)).afirst()

        if not connector or not chpt:
            return self._call_result.StartTransactionPayload(
                transaction_id=-1,
                id_tag_info=IdTagInfo(
                    status=AuthorizationStatus.blocked
                ).__dict__
            )

        ip_tran = await models.InProgressTransaction.objects.acreate(
            connector=connector, meter_start=meter_start, start_timestamp=timezone.now(),
            user_id=chpt.user_id, car_id=chpt.car_id
        )
        chpt.running = True
        chpt.transaction = ip_tran
        await chpt.asave(update_fields=['running', 'transaction'])

        return self._call_result.StartTransactionPayload(
            transaction_id=ip_tran.id, id_tag_info=IdTagInfo(status=AuthorizationStatus.accepted).__dict__
        )

    @on(action=Action.StopTransaction)
    async def on_stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        ipt = await models.InProgressTransaction.objects.filter(pk=transaction_id, end=False).select_related(
            'connector', 'connector__price_for_charge', 'user'
        ).afirst()

        if not ipt:
            return self._call_result.StopTransactionPayload(
                id_tag_info=IdTagInfo(status=AuthorizationStatus.invalid).__dict__)

        user = await CustomUser.objects.filter(pk=ipt.user_id).afirst()

        meter_used = meter_stop - ipt.meter_start
        final_price = meter_used * ipt.connector.price_for_charge.price
        end_time = timezone.now()

        ch_tr = await models.ChargeTransaction.objects.acreate(
            connector_id=ipt.connector_id, start_timestamp=ipt.start_timestamp, end_timestamp=end_time,
            meter_start=ipt.meter_start, meter_stop=meter_stop, duration=end_time - ipt.start_timestamp,
            meter_used=meter_used, start_token=ipt.start_token, cost=final_price, user_id=user.id
        )

        await UserBalanceHistory.objects.acreate(
            amount=final_price, user_id=user.id, operation=2, prev_balance=user.amount,
            new_balance=user.amount - final_price, title='Charging', connector_id=ipt.connector_id,
            charge_transaction_id=ch_tr.id
        )
        user.amount -= final_price
        await user.asave(update_fields=['amount'])
        ipt.end = True
        await ipt.asave(update_fields=['end'])
        return self._call_result.StopTransactionPayload(
            id_tag_info=IdTagInfo(status=AuthorizationStatus.accepted).__dict__)

    async def send_remote_start_transaction_command(self, connector_id: int, id_tag: str):
        payload = call.RemoteStartTransactionPayload(connector_id=int(connector_id), id_tag=str(id_tag))
        await self.call(payload=payload)

    async def send_remote_stop_transaction_command(self, transaction_id: int):
        payload = call.RemoteStopTransactionPayload(transaction_id=int(transaction_id))
        await self.call(payload=payload)

    @database_sync_to_async
    def __get_connector_price(self, connector: models.Connector):
        return connector
