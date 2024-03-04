from rest_framework import serializers
from datetime import datetime, timezone
from apps.core.models import Image


class OCPIResponseSerializer(serializers.Serializer):
    data = serializers.DictField()
    status_code = serializers.IntegerField()
    status_message = serializers.CharField(max_length=255)
    timestamp = serializers.DateTimeField(default=datetime.now(timezone.utc), read_only=True)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("url", "thumbnail", "category", "type", "width", "height")
