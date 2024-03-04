from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.locations.models import Location, ChargePoint, Connector
from apps.locations.serializers import LocationSerializer, ChargePointSerializer, ConnectorSerializer


class LocationListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = LocationSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = Location.objects.all()
        return queryset


class LocationDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        instance = self.get_object(kwargs.get('location_id'))

        serializer = LocationSerializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, location_id):
        return get_object_or_404(Location, id=location_id)


class ChargePointDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        instance = self.get_object(kwargs.get('location_id'), kwargs.get('evse_uid'))

        serializer = ChargePointSerializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, location_id, evse_uid):
        return get_object_or_404(ChargePoint, location_id=location_id, pk=evse_uid)


class ConnectorDetailAPIView(APIView):
    def get(self, request, *args, **kwargs):
        instance = self.get_object(kwargs.get('location_id'), kwargs.get('evse_uid'), kwargs.get('connector_id'))

        serializer = ConnectorSerializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, location_id, evse_uid, connector_id):
        return get_object_or_404(
            Connector,
            charge_point__location_id=location_id, charge_point_id=evse_uid, connector_id=connector_id
        )
