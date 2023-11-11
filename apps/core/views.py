from django.shortcuts import redirect
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_user_agents.utils import get_user_agent
from apps.accounts.models import QrCodeScanerCount


class AppRedirectAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(status=status.HTTP_302_FOUND, headers={"Location": "ztyapp://org.uicgroup.zty"})


class QRcodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        app_store = "apple store app url"
        play_market = "google play store app url"

        user_agent = get_user_agent(request)



        try:
            qr_count = QrCodeScanerCount.objects.last()
            if "Android" in user_agent or "Windows" in user_agent:
                qr_count.count += 1
                qr_count.android += 1
                qr_count.save()
                return redirect(play_market)
            elif "iOS" in user_agent or "Macintosh" in user_agent or "iPhone" in user_agent:
                qr_count.count += 1
                qr_count.iphone += 1
                qr_count.save()
                return redirect(app_store)
            else:
                qr_count.count += 1
                qr_count.save()
                return redirect(play_market)
        except Exception as e:
            QrCodeScanerCount.objects.create(count=0, iphone=0, android=0).save()
            qr_count = QrCodeScanerCount.objects.last()

            if "Android" in user_agent or "Windows" in user_agent:
                qr_count.count += 1
                qr_count.android += 1
                qr_count.save()
                return redirect(play_market)
            elif "iOS" in user_agent or "Macintosh" in user_agent or "iPhone" in user_agent:
                qr_count.count += 1
                qr_count.iphone += 1
                qr_count.save()
                return redirect(app_store)
            else:
                qr_count.count += 1
                qr_count.save()
                return redirect(play_market)
