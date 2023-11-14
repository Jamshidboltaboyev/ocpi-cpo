from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView)

from . import views


app_name = "accounts"

urlpatterns = [
    path("me", views.AccountView.as_view(), name="account-view"),
    path("sign-up/", views.CreateUserAPIView.as_view(), name="create-user"),
    path("image/upload/", views.UploadedImageCreateView.as_view(), name="image-upload"),
    path("image/delete/", views.DeleteImageView.as_view(), name="image-delete"),
    path("login/", views.LoginAPIView.as_view(), name="token_obtain_pair"),
    path("logout/", views.LogOutFromDeviceView.as_view(), name="user-logout-device"),
    path("refresh-token/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterView.as_view(), name="accounts_register"),  # todo
    path("activate/", views.ActivateView.as_view(), name="activate"),
    path("check-phone/", views.CheckPhoneView.as_view(), name="check-phone-number"),
    path("send-sms-code/", views.SendSmsCodeAPIView.as_view(), name="send-sms-code"),
    path("verify-sms-code/", views.VerifySMSCodeAPIView.as_view(), name="verify-sms-code"),
    path("reset-password/", views.ResetPasswordAPIView.as_view(), name="reset-password"),
    path("delete-profile/", views.DeleteProfileAPIView.as_view(), name="delete-profile"),
]
