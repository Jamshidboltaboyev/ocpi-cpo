from django.urls import path

from apps.versions.views import VersionListAPIView

urlpatterns = [
    path("", VersionListAPIView.as_view())
]
