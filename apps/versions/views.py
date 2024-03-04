from datetime import datetime, timezone

from drf_yasg.utils import swagger_auto_schema

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import OCPIResponseSerializer


class VersionListAPIView(APIView):
    @swagger_auto_schema(tags=["Versions"])
    def get(self, request, *args, **kwargs):
        versions = {
            "data": [
                {
                    "version": "2.2.1",
                    "url": "http://localhost:8000/ocpi/2.2.1/details"
                }
            ],
            "status_code": 1000,
            "status_message": "Generic success code",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return Response(versions)


class VersionV2_2_1_DetailAPIView(APIView):
    @swagger_auto_schema(tags=["Versions"])
    def get(self, request, *args, **kwargs):
        details = {
            "data": {
                "version": "2.2.1",
                "endpoints": [
                    {
                        "identifier": "locations",
                        "role": "SENDER",
                        "url": "https://www.example.com/ocpi/cpo/2.2.1/locations"
                    },
                    {
                        "identifier": "sessions",
                        "role": "SENDER",
                        "url": "https://www.example.com/ocpi/cpo/2.2.1/sessions"
                    },
                    {
                        "identifier": "credentials",
                        "role": "RECEIVER",
                        "url": "https://www.example.com/ocpi/cpo/2.2.1/credentials"
                    },
                    {
                        "identifier": "tariffs",
                        "role": "SENDER",
                        "url": "https://www.example.com/ocpi/cpo/2.2.1/tariffs"
                    },
                    {
                        "identifier": "cdrs",
                        "role": "SENDER",
                        "url": "https://www.example.com/ocpi/cpo/2.2.1/cdrs"
                    },
                    {
                        "identifier": "tokens",
                        "role": "RECEIVER",
                        "url": "https://www.example.com/ocpi/cpo/2.2.1/tokens"
                    },
                    {
                        "identifier": "credentials",
                        "role": "RECEIVER",
                        "url": "https://www.example.com/ocpi/emsp/2.2.1/credentials"
                    },
                    {
                        "identifier": "locations",
                        "role": "RECEIVER",
                        "url": "https://www.example.com/ocpi/emsp/2.2.1/locations"
                    },
                    {
                        "identifier": "sessions",
                        "role": "RECEIVER",
                        "url": "https://www.example.com/ocpi/emsp/2.2.1/sessions"
                    },
                    {
                        "identifier": "cdrs",
                        "role": "RECEIVER",
                        "url": "https://www.example.com/ocpi/emsp/2.2.1/cdrs"
                    },
                    {
                        "identifier": "tariffs",
                        "role": "RECEIVER",
                        "url": "https://www.example.com/ocpi/emsp/2.2.1/tariffs"
                    },
                    {
                        "identifier": "commands",
                        "role": "SENDER",
                        "url": "https://www.example.com/ocpi/emsp/2.2.1/commands"
                    },
                    {
                        "identifier": "tokens",
                        "role": "SENDER",
                        "url": "https://www.example.com/ocpi/emsp/2.2.1/tokens"
                    }
                ]
            },
            "status_code": 1000,
            "status_message": "Generic success code",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return Response(details)
