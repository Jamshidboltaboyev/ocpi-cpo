from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Image
from apps.credentials.models import Credentials, CredentialsRole, BusinessDetails
from apps.credentials.serializers import CredentialsSerializer


class CredentialsAPIView(APIView):
    @swagger_auto_schema(tags=["Credentials module"])
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = CredentialsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        qs = Credentials.objects.prefetch_related('roles', 'roles__business_details', "roles__business_details__logo")
        return qs

    @swagger_auto_schema(tags=["Credentials module"])
    def post(self, request, *args, **kwargs):
        data = request.data

        credentials = Credentials.objects.create(token=data['token'], url=data['url'])
        for role in data['roles']:
            logo, created = Image.objects.get_or_create(
                url=role['business_details']['logo']['url'],
                defaults={
                    "url": role['business_details']['logo']['url'],
                    "thumbnail": role['business_details']['logo']['thumbnail'],
                    "category": role['business_details']['logo']['category'],
                    "type": role['business_details']['logo']['type'],
                    "width": role['business_details']['logo']['width'],
                    "height": role['business_details']['logo']['height']
                }
            )

            CredentialsRole.objects.create(
                credentials_id=credentials.id,
                role=role['role'],
                business_details=BusinessDetails.objects.get_or_create(
                    name=role['business_details']['name'], defaults={
                        "name": role['business_details']['name'],
                        "website": role['business_details']['website'],
                        "logo": logo
                    }
                )[0],
                party_id=role['party_id'],
                country_code=role['country_code']
            )

        return




