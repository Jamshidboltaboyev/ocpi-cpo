from django.urls import path

from apps.locations.views import LocationListAPIView

urlpatterns = [
    path("", LocationListAPIView.as_view())
]
