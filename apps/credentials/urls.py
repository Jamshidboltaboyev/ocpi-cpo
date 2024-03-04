from django.urls import path

from apps.credentials.views import CredentialsAPIView

urlpatterns = [
    path("", CredentialsAPIView.as_view())
]
