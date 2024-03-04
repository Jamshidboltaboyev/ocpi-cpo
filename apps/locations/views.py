from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.locations.models import Location
from apps.locations.serializers import LocationSerializer


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
