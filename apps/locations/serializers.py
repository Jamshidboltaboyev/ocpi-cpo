from django.conf import settings
from rest_framework import serializers

from apps.locations.models import Location, PublishTokenType, ChargePoint, Connector


class PublishTokenTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishTokenType
        fields = ("uid", "type")


class GeoLocationSerializer(serializers.Serializer):
    latitude = serializers.CharField(max_length=10)
    longitude = serializers.CharField(max_length=11)


class ConnectorSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='connector_id')
    tariff_ids = serializers.ListSerializer(child=serializers.CharField(max_length=10), default=[])

    class Meta:
        model = Connector
        fields = (
            "id", "standard", "format", "power_type", "max_voltage", "max_amperage",
            "max_electric_power", "tariff_ids", "status"
        )


class ChargePointSerializer(serializers.ModelSerializer):
    uid = serializers.CharField(source='id')
    evse_id = serializers.CharField(source='id')
    connectors = serializers.SerializerMethodField(method_name='get_connectors')
    last_updated = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = ChargePoint
        fields = ("status", "connectors", "last_updated", 'uid', "evse_id")

    def get_connectors(self, obj: ChargePoint):
        qs = Connector.objects.filter(charge_point_id=obj.id)
        return ConnectorSerializer(qs, many=True).data


class LocationSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(default="UZ", read_only=True)
    party_id = serializers.CharField(default=settings.CPO_PARTY_ID, read_only=True)
    postal_code = serializers.CharField(default="100001", read_only=True)
    related_locations = serializers.ListSerializer(
        child=serializers.CharField(max_length=10), default=[], read_only=True
    )
    directions = serializers.ListSerializer(
        child=serializers.CharField(max_length=10), default=[], read_only=True
    )
    facilities = serializers.ListSerializer(
        child=serializers.CharField(max_length=10), default=[], read_only=True
    )
    time_zone = serializers.CharField(default=settings.TIME_ZONE)

    publish_allowed_to = PublishTokenTypeSerializer(many=True)
    evses = serializers.SerializerMethodField(method_name="get_evses")

    city = serializers.CharField(source='district.region.name')
    state = serializers.CharField(source='district.name')
    country = serializers.CharField(source='district.region.country.ico_code')
    last_updated = serializers.DateTimeField(source='updated_at')
    coordinates = serializers.SerializerMethodField(method_name='get_coordinates')

    class Meta:
        model = Location
        fields = (
            "country_code", "party_id", "id", "publish_allowed_to", "name", "address",
            "city", "state", "country", "coordinates", "parking_type", "last_updated",
            "directions", "time_zone", "postal_code", "facilities", "related_locations",
            "evses"
        )

    def get_coordinates(self, obj: Location):
        return {
            "latitude": obj.latitude,
            "longitude": obj.longitude
        }

    def get_evses(self, obj: Location):
        qs = ChargePoint.objects.filter(location_id=obj.id)

        return ChargePointSerializer(qs, many=True).data
