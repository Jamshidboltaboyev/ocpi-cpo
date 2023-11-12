import requests
import datetime

from apps.accounts.models import OTP

SEND_URL = 'http://91.204.239.44/broker-api/send'
LOGIN = 'yoki'
PASSWORD = '57;%3UT!zKhx'


def send_single_sms(sms: OTP):
    if sms.phone_number in ['+998901231212', '+998712007007', "+998996488450"]:
        return
    sms_data = {'messages': {"recipient": sms.phone_number, "message-id": sms.message_id,
                             "sms": {"originator": "UIC", "content": {"text": sms.text}}}}
    response = requests.post(SEND_URL, json=sms_data, auth=(LOGIN, PASSWORD))
    if response.text == 'Request is received':
        sms.is_sent = True
        sms.sent_at = datetime.datetime.now()
        sms.save(update_fields=['is_sent', 'sent_at'])
