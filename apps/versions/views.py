from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import OCPIResponseSerializer


class VersionListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        versions = {

        }

        response = OCPIResponseSerializer(data=versions)
        return Response(data=response)
