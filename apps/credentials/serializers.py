from rest_framework import serializers

from apps.core.serializers import ImageSerializer
from apps.credentials.models import Credentials, BusinessDetails, CredentialsRole


class BusinessDetailsSerializer(serializers.ModelSerializer):
    logo = ImageSerializer()

    class Meta:
        model = BusinessDetails
        fields = ("name", 'website', "logo")


class CredentialsRoleSerializer(serializers.ModelSerializer):
    business_details = BusinessDetailsSerializer()

    class Meta:
        model = CredentialsRole
        fields = ("role", "party_id", "country_code", "business_details")


class CredentialsSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField(method_name='get_roles')

    class Meta:
        model = Credentials
        fields = ("token", "url", "roles")

    def get_roles(self, obj: Credentials):
        qs = CredentialsRole.objects.filter(credentials_id=obj.id)
        return CredentialsRoleSerializer(qs, many=True).data
