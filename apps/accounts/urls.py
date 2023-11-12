from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView)

from apps.accounts import views

app_name = 'accounts'

auth_urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="token_obtain_pair"),
    path("refresh-token/", TokenRefreshView.as_view(), name="token_refresh"),

    path("check-phone/", views.CheckPhoneView.as_view(), name="check-phone-number"),
    path("forgot-password/", views.ForgotPasswrdAPIView.as_view()),
    path("logout/", views.LogOutFromDeviceView.as_view(), name="user-logout-device"),
    path("register/", views.RegisterView.as_view(), name="accounts_register"),
    path("activate/", views.ActivateView.as_view(), name="activate"),
]


urlpatterns = [
    path("me/", views.AccountView.as_view(), name="account-view"),

    path("image/upload/", views.UploadedImageCreateView.as_view(), name="image-upload"),
    path("image/delete/", views.DeleteImageView.as_view(), name="image-delete"),

    path("send-sms-code/", views.SendSmsCodeAPIView.as_view(), name="send-sms-code"),
    path("verify-sms-code/", views.SendSmsCodeAPIView.as_view(), name="verify-sms-code"),

    path("delete-profile/", views.DeleteProfileApiView.as_view(), name="delete-profile"),
] + auth_urlpatterns
