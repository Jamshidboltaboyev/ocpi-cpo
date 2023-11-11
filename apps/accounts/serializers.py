from django.core.cache import cache
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from phonenumber_field.phonenumber import to_python
from accounts.cache import CacheTypes, types
from accounts.models import DeletedAccount
from core.models import UploadedImage
from utils.user_auth import AuthService
from .models import User, Otp


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ("image",)


class DeleteImageSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "full_name", "birth_date", "phone", "amount", "avatar", "image_url", "birth_date_editable")
        read_only_fields = ["id"]

    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.avatar:
            return obj.avatar.image.url

    birth_date = serializers.DateField(format="%d.%m.%Y", required=False, read_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(required=True)

    class Meta:
        model = User
        fields = ("phone",)


class CheckPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(help_text='String with +')


class ActivateSerializer(serializers.Serializer):
    phone = serializers.CharField()
    register = serializers.CharField(allow_null=True, allow_blank=True)
    imei_code = serializers.CharField()
    code = serializers.CharField()
    full_name = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if len(attrs.get("password")) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters", code="invalid_password")


class LogoutSerializer(serializers.Serializer):
    imei_code = serializers.CharField()


class SendSmsCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(help_text='String with +')
    type = serializers.CharField()

    def validate_type(self, value):
        if value not in types:
            raise serializers.ValidationError("Invalid type", code="invalid_type")
        return value

    def validate_phone(self, value):
        if not to_python(value).is_valid():
            raise serializers.ValidationError(code='invalid_phone', detail='Нотўғри номер')
        return value

    def validate(self, attrs):
        phone = attrs.get("phone")
        type_ = attrs.get("type")
        cache_keys = cache.keys(f"{type_}{str(phone)}*")
        if cache_keys:
            raise serializers.ValidationError("Code already sent", code="code_already_sent")
        return attrs


class DeletedProfileSerializer(serializers.ModelSerializer):
    reason = serializers.CharField()
    code = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = DeletedAccount
        fields = ["reason", "code"]

    def validate(self, attrs):
        type_ = CacheTypes.delete_profile
        request = self.context.get("request")
        phone = request.user.phone

        is_blocked = AuthService.is_user_blocked(phone=phone, type_=type_)
        if is_blocked:
            raise serializers.ValidationError("User is blocked", code="blocked_user")

        if not Otp.check_code(phone, request.data["code"], type_=type_):
            AuthService.check_login_attempts(phone=phone, type_=type_)
            raise serializers.ValidationError("Code is invalid", code="invalid_code")
        AuthService.reset_login_attempts(phone=phone, type_=type_)
        return attrs

    def create(self, validated_data):
        user = self.context.get("request").user
        validated_data["user"] = user
        validated_data["phone"] = user.phone
        validated_data["first_name"] = user.first_name
        validated_data["last_name"] = user.last_name
        validated_data.pop("code")
        return super().create(validated_data)


class ForgotPasswordSerializer(serializers.Serializer):
    phone = PhoneNumberField(required=True)

    def validate_phone(self, value):
        if not User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(detail="Phone doesn't exists")
        return value
