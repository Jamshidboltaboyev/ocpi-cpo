import datetime
from datetime import timedelta

import requests
from celery import shared_task
from django.utils import timezone

from apps.accounts.models import User, UserGift


def send_single_sms(smid):
    from apps.accounts.models import OTP

    # try:
    #     message = OTP.objects.get(pk=smid)
    #     sms = {
    #         "messages": {
    #             "recipient": message.recipient,
    #             "message-id": message.message_id,
    #             "sms": {"originator": "3700", "content": {"text": message.text}},
    #         }
    #     }
    #     response = requests.post(SEND_URL, json=sms, auth=(LOGIN, PASSWORD))
    #     if response.text == "Request is received":
    #         message.sent = True
    #         message.sent_time = datetime.datetime.now()
    #         message.save()
    # except Exception as e:
    #     print(e)
    #


@shared_task
def create_user_gifts():
    today = timezone.now().date()
    users_with_birthdate = User.objects.filter(birth_date__month=today.month, birth_date__day=today.day)

    for user in users_with_birthdate:
        UserGift.objects.create(user=user, expired_date=today + timedelta(days=3))
        user.balance += 50000
        user.save()


@shared_task
def check_user_gift_status():
    active_user_gifts = UserGift.objects.filter(
        status=UserGift.GiftStatus.ACTIVE, expired_date__lt=timezone.now().date()
    )

    for user_gift in active_user_gifts:
        user_gift.status = UserGift.GiftStatus.EXPIRED
        user_gift.save()
        user_gift.user.balance -= 50000
        user_gift.user.save()


@shared_task
def daily_user_gift_check():
    create_user_gifts.delay()
    check_user_gift_status.delay()
