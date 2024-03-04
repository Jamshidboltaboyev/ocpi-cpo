from django.urls import path

from apps.locations.views import LocationListAPIView, LocationDetailAPIView

urlpatterns = [
    path("", LocationListAPIView.as_view()),
    path("<str:location_id>/", LocationDetailAPIView.as_view())
]
