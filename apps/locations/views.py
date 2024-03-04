from rest_framework import status
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
