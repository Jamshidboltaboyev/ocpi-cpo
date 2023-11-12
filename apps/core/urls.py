from django.urls import path

from .views import AppRedirectAPIView, QRcodeView

app_name = 'core'

urlpatterns = [
    path("deeplink/", AppRedirectAPIView.as_view(), name="AppRedirect"),
    path("qrcode/", QRcodeView.as_view(), name="QRcodeView"),

]
