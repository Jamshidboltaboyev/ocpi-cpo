from rest_framework import serializers
from datetime import datetime, timezone


class OCPIResponseSerializer(serializers.Serializer):
    data = serializers.DictField()
    status_code = serializers.IntegerField()
    status_message = serializers.CharField(max_length=255)
    timestamp = serializers.DateTimeField(default=datetime.now(timezone.utc), read_only=True)
