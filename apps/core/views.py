import os

from django.shortcuts import redirect
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_user_agents.utils import get_user_agent
from .models import QrCodeScanerCount
from user_agents.parsers import UserAgent


class AppRedirectAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_302_FOUND, headers={"Location": "ztyapp://org.uicgroup.zty"})


class QRcodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        app_store = os.getenv("APPLE_STORE_APP_URL", "")
        redirect_url = os.getenv("GOOGLE_PLAY_STORE_APP_URL", "")  # default play market

        user_agent: UserAgent = get_user_agent(request)
        qr_count = QrCodeScanerCount.objects.get_or_create()

        if user_agent.os.family in ["Android", 'Windows']:
            qr_count.android += 1
        elif user_agent in ['iOS', 'Macintosh', 'iPhone']:
            qr_count.iphone += 1
            redirect_url = app_store

        qr_count.count += 1
        qr_count.save(update_fields=['count', 'iphone', 'android'])

        return redirect(redirect_url)
