from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from apps.accounts import views

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # done
    path("forgot-password/", views.ForgotPasswrdAPIView.as_view()),



    path("me/", views.AccountView.as_view(), name="account-view"),
    path("image/upload/", views.UploadedImageCreateView.as_view(), name="image-upload"),
    path("image/delete/", views.DeleteImageView.as_view(), name="image-delete"),

    path("send-sms-code/", views.SendSmsCodeView.as_view(), name="send-sms-code"),
    path("verify-sms-code/", views.SendSmsCodeView.as_view(), name="verify-sms-code"),

    path("logout/", views.LogOutFromDeviceView.as_view(), name="user-logout-device"),
    path("refresh-token/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterView.as_view(), name="accounts_register"),
    path("activate/", views.ActivateView.as_view(), name="activate"),
    path("check-phone/", views.CheckPhoneView.as_view(), name="check-phone-number"),
    path("delete-profile/", views.DeleteProfileApiView.as_view(), name="delete-profile"),
]
