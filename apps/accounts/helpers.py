import requests
import datetime

SEND_URL = 'http://91.204.239.44/broker-api/send'
LOGIN = 'yoki'
PASSWORD = '57;%3UT!zKhx'


def send_single_sms(sm):
    sms = {'messages': {"recipient": sm.recipient, "message-id": sm.message_id,
                        "sms": {"originator": "UIC", "content": {"text": sm.text}}}}
    response = requests.post(SEND_URL, json=sms, auth=(LOGIN, PASSWORD))
    if response.text == 'Request is received':
        sm.sent = True
        sm.sent_time = datetime.datetime.now()
        sm.save()


sms = {'messages': {"recipient": "+998996488450", "message-id": 1,
                    "sms": {"originator": "UIC", "content": {"text": "UIC Tasdiqlash kodi 530569"}}}}
response = requests.post(SEND_URL, json=sms, auth=(LOGIN, PASSWORD))
