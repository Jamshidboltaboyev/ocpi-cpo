from django.urls import path

from apps.locations.views import (
    LocationListAPIView,
    LocationDetailAPIView,
    ChargePointDetailAPIView,
    ConnectorDetailAPIView
)

urlpatterns = [
    path("", LocationListAPIView.as_view()),
    path("<str:location_id>/", LocationDetailAPIView.as_view()),
    path("<str:location_id>/<str:evse_uid>/", ChargePointDetailAPIView.as_view()),
    path("<str:location_id>/<str:evse_uid>/<str:connector_id>/", ConnectorDetailAPIView.as_view()),
]
