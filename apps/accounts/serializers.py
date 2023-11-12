from django.core.cache import cache
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from phonenumber_field.phonenumber import to_python
from .cache import OTPTypes, otp_types
from .models import DeletedAccount
from apps.core.models import Media
from apps.accounts.utils.user_auth import AuthService
from .models import User, OTP


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ("image",)


class DeleteImageSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "full_name", "birth_date", "phone", "balance", "avatar", "image_url", "birth_date_editable")
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


class SignUpSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    imei_code = serializers.CharField(required=True)
    session = serializers.CharField(required=True)
    full_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if len(attrs.get("password")) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters", code="invalid_password")

    def validate_phone(self, value):
        if not to_python(value).is_valid():
            raise serializers.ValidationError(code='invalid_phone', detail='Нотўғри номер')
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters", code="invalid_password")
        return value


class LogoutSerializer(serializers.Serializer):
    imei_code = serializers.CharField()


class SendSmsCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, help_text='String with +')
    otp_type = serializers.CharField(required=True)

    def validate_otp_type(self, value):
        if value not in otp_types:
            raise serializers.ValidationError("Invalid type", code="invalid_otp_type")
        return value

    def validate_phone(self, value):
        if not to_python(value).is_valid():
            raise serializers.ValidationError(code='invalid_phone', detail='Нотўғри номер')
        return value

    def validate(self, attrs):
        phone = attrs.get("phone")
        otp_type = attrs.get("otp_type")

        for_phone_availability = [
            OTPTypes.REGISTRATION_SMS_VERIFICATION,
            OTPTypes.UPDATE_PHONE_VERIFICATION,
        ]
        for_phone_existence = [
            OTPTypes.LOGIN_SMS_VERIFICATION,
            OTPTypes.FORGET_PASS_VERIFICATION,
            OTPTypes.CHANGE_PASSWORD,
            OTPTypes.DELETE_PROFILE,
        ]

        qs = User.objects.filter(phone=phone, is_deleted=False)

        if otp_type in for_phone_availability:
            if qs.exists():
                raise serializers.ValidationError(
                    code='phone_exists', detail="User already exists with this phone number"
                )
        elif otp_type in for_phone_existence:
            if not qs.exists():
                return False, serializers.ValidationError(
                    code="phone_not_found", detail="User not found with this phone number"
                )

        if AuthService.is_user_blocked(phone, otp_type):
            raise serializers.ValidationError("User is blocked", code="blocked_user")

        return attrs


class DeletedProfileSerializer(serializers.ModelSerializer):
    reason = serializers.CharField()
    code = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = DeletedAccount
        fields = ["reason", "code"]

    def validate(self, attrs):
        type_: str = OTPTypes.DELETE_PROFILE.value
        request = self.context.get("request")
        phone = request.user.phone

        is_blocked = AuthService.is_user_blocked(phone=phone, type=type_)
        if is_blocked:
            raise serializers.ValidationError("User is blocked", code="blocked_user")

        if not OTP.check_code(phone, request.data["code"], type_=type_):
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


class VerifySMSCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    session = serializers.CharField(required=True)
    otp_type = serializers.CharField(required=True)

    def validate_otp_type(self, value):
        if value not in otp_types:
            raise serializers.ValidationError("Invalid type", code="invalid_type")
        return value

    def validate_phone(self, value):
        phone = to_python(value)
        if not phone.is_valid():
            raise serializers.ValidationError(code='invalid_phone', detail='Нотўғри номер')
        return phone
