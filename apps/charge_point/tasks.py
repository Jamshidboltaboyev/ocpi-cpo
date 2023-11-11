import datetime
import time
from datetime import date, timedelta

import requests
from celery import shared_task
from django.db.models import Q, Sum
from payments import PaymentStatus

from apps.charge_point.models import Address, ChargePoint, ChargeTransaction
from apps.payment.models import Provider, Transaction


@shared_task(name="reserve_now")
def reserve_now(connector_id):
    print(connector_id)


def send_msg(message):
    pass
    # token = "6303416189:AAFp5aVOEkdKy0Qzu8--OcZ07s4UriOv6_E"  # @Charge_informer_bot
    # channel_id = -1001909042916  # ZTY statistic
    # url = f"https://api.telegram.org/bot{token}/sendMessage"
    # params = {"chat_id": channel_id, "text": message}
    # #requests.post(url, data=params)


def transaction_report(date):
    send_msg("✅✅✅✅✅✅✅✅✅✅✅✅✅✅")
    q_filter = (
        Q(variant=Provider.PAYLOV)
        | Q(variant=Provider.PAYME)
        | Q(variant=Provider.CLICK)
        | Q(variant=Provider.CARD)
        | Q(variant=Provider.UZUM_BANK)
    )
    transactions = Transaction.objects.filter(Q(created_at__date=date, status=PaymentStatus.CONFIRMED) & q_filter)
    if transactions.count() == 0:
        send_msg("Bugunlik to'lovlar yo'q")
        return "no transactions"
    transaction_count = transactions.count()  # umumiy transactionlar soni
    total_amount = transactions.aggregate(total_amount=Sum("total"))["total_amount"]  # umumiy summa
    payme_amount = transactions.filter(variant=Provider.PAYME).aggregate(total_amount=Sum("total"))[
        "total_amount"
    ]  # payme summa
    payme_count = transactions.filter(variant=Provider.PAYME).count()  # payme count
    click_amount = transactions.filter(variant=Provider.CLICK).aggregate(total_amount=Sum("total"))[
        "total_amount"
    ]  # click summa
    click_count = transactions.filter(variant=Provider.CLICK).count()  # click count
    paylov_amount = transactions.filter(variant=Provider.PAYLOV).aggregate(total_amount=Sum("total"))[
        "total_amount"
    ]  # paylov summa
    paylov_count = transactions.filter(variant=Provider.PAYLOV).count()  # paylov count
    uzum_bank_amount = transactions.filter(variant=Provider.UZUM_BANK).aggregate(total_amount=Sum("total"))[
        "total_amount"
    ]  # uzum_bank summa
    uzum_bank_count = transactions.filter(variant=Provider.UZUM_BANK).count()  # uzum_bank count
    card_amount = transactions.filter(variant=Provider.CARD).aggregate(total_amount=Sum("total"))[
        "total_amount"
    ]  # card summa
    card_count = transactions.filter(variant=Provider.CARD).count()  # card count

    if card_amount is None:
        card_amount = 0
    if payme_amount is None:
        payme_amount = 0
    if paylov_amount is None:
        paylov_amount = 0
    if click_amount is None:
        click_amount = 0
    if card_amount is None:
        card_amount = 0

    # send message
    message = (
        f"✅🅰️Kunlik hisobot :\n"
        f"🚗 Muassasa: ZTY car energy \n"
        f"🗓 Hisobot kuni: {date}\n"
        f"----------\n"
        f"Jami buyurtmalar soni: {transaction_count} ta\n"
        f"💵 Card : {card_amount} soʻm --{card_count} ta to'lov\n"
        f"💳 Payme : {payme_amount} soʻm --{payme_count} ta to'lov\n"
        f"💳 Click : {click_amount} soʻm -{click_count} ta to'lov\n"
        f"💳 Paylov : {paylov_amount} soʻm -{paylov_count} ta to'lov\n"
        f"💳 Uzum Bank : {uzum_bank_amount} soʻm --{uzum_bank_count} ta to'lov\n"
        f"💰 Jami kirim: {total_amount} soʻm "
    )
    send_msg(message)  # send message
    return str(date)


def transaction_charge_point_report(date):
    message = ""
    transactions = ChargeTransaction.objects.filter(start_timestamp__date=date)
    if transactions.count() == 0:
        return "No transactions"
    transaction_count = transactions.count()  # Umumiy transactionlar soni
    total_meter_used = transactions.aggregate(total_meter_used=Sum("meter_used"))[
        "total_meter_used"
    ]  # Umumiy ishlatilgan kw
    total_cost = transactions.aggregate(total_cost=Sum("cost"))["total_cost"]  # Umumiy to'langan summa

    message += f"✅🅱️Stansiyalar statistikasi {date}\n"
    message += f"🔢 Umumiy zaryadlash soni: {transaction_count} ta\n"
    message += f"📏 Umumiy ishlatilgan tok: {total_meter_used} kW\n"
    message += f"💲 Umumiy to'langan summa: {total_cost} sum\n"
    send_msg(message)
    # Adresslar va ChargePoint'lar uchun statistika
    addresses = Address.objects.all()
    for address in addresses:
        charge_points = ChargePoint.objects.filter(address=address)
        point_transactions = transactions.filter(connector__charge_point__in=charge_points)
        if point_transactions.count() > 0:
            message_single = ""
            message_single += f"\n🏢 Manzil: {address.name}\n"
            for charge_point in charge_points:
                point_count = point_transactions.filter(connector__charge_point=charge_point).count()
                if point_count > 0:
                    point_meter_used = point_transactions.filter(connector__charge_point=charge_point).aggregate(
                        total_meter_used=Sum("meter_used")
                    )["total_meter_used"]
                    point_cost = point_transactions.filter(connector__charge_point=charge_point).aggregate(
                        total_cost=Sum("cost")
                    )["total_cost"]
                    message_single += f"📍 Stansiya: {charge_point.name}\n"
                    message_single += f"🔢 Zaryadlash soni: {point_count}\n"
                    message_single += f"📏 Ishlatilgan tok: {point_meter_used} kW\n"
                    message_single += f"💲 To'langan summa: {point_cost} sum\n"
                    message_single += "------------------------\n"
            send_msg(message_single)
    return f"Hisobot muvaffaqiyatli yuborildi {date}"


@shared_task
def daily_transaction_report():
    yesterday = datetime.now().date() - timedelta(days=1)
    transaction_report(yesterday)


@shared_task
def daily_transaction_report_charge_point():
    yesterday = datetime.now().date() - timedelta(days=1)
    transaction_charge_point_report(yesterday)


@shared_task
def history_transaction_report_charge_point():
    start_date = date(2023, 10, 10)
    end_date = date.today()
    current_date = start_date
    while current_date < end_date:
        transaction_report(current_date)
        transaction_charge_point_report(current_date)
        current_date += timedelta(days=1)
        print(current_date)
        time.sleep(5)
