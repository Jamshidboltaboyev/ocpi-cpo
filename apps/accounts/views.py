import datetime

import phonenumbers
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .cache import otp_types, OTPTypes
from apps.accounts.helpers import send_single_sms
from apps.accounts.models import User, OTP, UserLoginDevice
from apps.accounts.serializers import (ActivateSerializer, CheckPhoneSerializer,
                                       CreateUserSerializer,
                                       DeletedProfileSerializer,
                                       DeleteImageSerializer, LogoutSerializer,
                                       ResetPasswordSerializer,
                                       SendSmsCodeSerializer,
                                       UploadedImageSerializer, UserSerializer,
                                       UserWithMinBalanceSerializer,
                                       VerifySMSCodeSerializer)
from apps.core.models import Media
from utils.user_auth import AuthService


class UploadedImageCreateView(generics.CreateAPIView):
    queryset = Media.objects.all()
    serializer_class = UploadedImageSerializer
    parser_classes = (MultiPartParser,)

    def create(self, request, *args, **kwargs):
        image_serializer = UploadedImageSerializer(data=request.data)
        if image_serializer.is_valid():
            uploaded_image = image_serializer.save()  # Save the uploaded image instance
            return Response(
                {"id": uploaded_image.id}, status=status.HTTP_201_CREATED
            )  # Access the ID of the saved instance
        else:
            return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteImageView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DeleteImageSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.request.user.id)
        validated_data = DeleteImageSerializer(data=request.data)
        validated_data.is_valid(raise_exception=True)
        avatar_id = validated_data.validated_data["pk"]
        if user.avatar_id == avatar_id:
            user.avatar = None
            user.save()
            image = Media.objects.get(pk=avatar_id)
            image.delete()

            return Response({"status": "image o'chirildi"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "ushbu id da rasm topilmadi"}, status=status.HTTP_400_BAD_REQUEST)


class AccountView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    allowed_method = ["GET", "POST"]

    def get(self, request):

        """
        # get current request user
        """
        self.queryset = self.queryset.get(pk=request.user.id)
        serializer = UserWithMinBalanceSerializer(self.queryset, read_only=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "full_name": openapi.Schema(type=openapi.TYPE_STRING, description="String"),
                "birth_date": openapi.Schema(type=openapi.TYPE_STRING, description="format DD.MM.YYYY"),
                "phone": openapi.Schema(type=openapi.TYPE_STRING, description="with +"),
                "avatar_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="image file"),
            },
        )
    )
    def post(self, request):
        """
        # edit current request user full_name and birth_date and phone number

        agar yangi raqam kiritilsa, sms yuboriladi
        keying activate/  apiga
        {
              "phone": "yangi  raqam",
              "change_phone": true,
              "imei_code": "12312321",
              "code": "otp kod"
            }

            YUBORILADI VA TOKEN QAYTARILADI
        """
        if request.data["full_name"] is not None and request.data["birth_date"] is not None:

            if request.data["avatar_id"] == 0:
                print("avatar_id=0")
                birth_date = datetime.datetime.strptime(request.data["birth_date"], "%d.%m.%Y").strftime("%Y-%m-%d")
                user = self.queryset.get(pk=request.user.id)
                user.full_name = request.data["full_name"]
                user.birth_date = birth_date
                user.birth_date_editable = False
                user.avatar = None
                user.save()

            elif request.data["avatar_id"] is not None and request.data["avatar_id"] != 0:
                if Media.objects.filter(pk=request.data["avatar_id"]).exists():
                    birth_date = datetime.datetime.strptime(request.data["birth_date"], "%d.%m.%Y").strftime("%Y-%m-%d")
                    user = self.queryset.get(pk=request.user.id)
                    user.full_name = request.data["full_name"]
                    user.birth_date = birth_date
                    user.birth_date_editable = False
                    user.avatar_id = request.data["avatar_id"]
                    user.save()
                else:
                    return Response(
                        {"status": "error", "message": "Rasm topilmadi"}, status=status.HTTP_400_BAD_REQUEST
                    )

            if "phone" in request.data:
                try:
                    phone = phonenumbers.parse(request.data["phone"])
                except Exception:
                    return Response({"status": "error", "message": "Нотўғри номер"}, status=status.HTTP_400_BAD_REQUEST)

                if phonenumbers.is_possible_number(phone):
                    changed_phone = False
                    if User.objects.filter(phone=request.data["phone"]).exists():
                        return Response(
                            {"status": "error", "message": "Рақам тизимда мавжуд"}, status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        if request.data["phone"] != user.phone:
                            changed_phone = True
                            # code = '111111'
                            code = get_random_string(6, allowed_chars="0123456789")
                            text = "UIC Tasdiqlash kodi {}".format(code)
                            sm = OTP.create_message(
                                request.data["phone"], text, user, code, request.META["REMOTE_ADDR"]
                            )
                            send_single_sms(sm)

                    return Response(
                        {"status": "success", "data": UserSerializer(user).data, "send_code": changed_phone},
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response({"status": "success", "data": UserSerializer(user).data}, status=status.HTTP_200_OK)

        else:
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    queryset = OTP.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = CheckPhoneSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone": openapi.Schema(type=openapi.TYPE_STRING, description="String with +"),
            },
        )
    )
    def post(self, request):
        """
        # register user
        """
        phone = ""

        is_blocked = AuthService.is_user_blocked(
            phone=request.data["phone"], type=CacheTypes.registration_sms_verification
        )
        if is_blocked:
            raise serializers.ValidationError("User is blocked", code="blocked_user")

        try:
            phone = phonenumbers.parse(request.data["phone"])
        except Exception:
            return Response({"status": "error", "message": "Нотўғри номер"}, status=status.HTTP_400_BAD_REQUEST)

        if phonenumbers.is_possible_number(phone):
            if User.objects.filter(phone=phone).exists():
                return Response(
                    {"status": "error", "message": "Бу рақам тизимда мавжуд"}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                sms = OTP.objects.filter(
                    recipient=request.data["phone"], add_time__gte=(timezone.now() - datetime.timedelta(minutes=1))
                ).last()
                if sms:
                    time_to_retry = 60 - int((timezone.now() - sms.add_time).total_seconds())
                    return Response({"sec_to_retry": time_to_retry}, status=status.HTTP_200_OK)
                else:
                    user = None
                    if request.user.is_authenticated:
                        user = request.user
                    code = get_random_string(6, allowed_chars="0123456789")

                    # test uchun code
                    text = "UIC Tasdiqlash kodi {}".format(code)
                    if request.data["phone"] == "+998901231212" or request.data["phone"] == "+998712007007":
                        code = "081020"
                    sm = OTP.create_message(
                        request.data["phone"], text, user, code, request.META["REMOTE_ADDR"]
                    )
                    send_single_sms(sm)
                    return Response({"sec_to_retry": 60}, status=status.HTTP_200_OK)

        else:
            return Response({"status": "error", "message": "Нотўғри номер"}, status=status.HTTP_400_BAD_REQUEST)


class CreateUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)

        device = UserLoginDevice()
        device.user = user
        device.imei_code = serializer.validated_data.get("imei_code", None)
        device.model_name = serializer.validated_data.get("model_name", None)
        device.login_time = timezone.now()
        device.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "status": "success",
                "message": "Мувофаққиятли рўйхатдан ўтилди",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
            headers=headers,
        )


class ActivateView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ActivateSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone": openapi.Schema(type=openapi.TYPE_STRING, description="String with +"),
                "register": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="when registering True"),
                "imei_code": openapi.Schema(type=openapi.TYPE_STRING, description="user mobile phone imei code"),
                "code": openapi.Schema(type=openapi.TYPE_STRING, description="sms code"),
                "full_name": openapi.Schema(type=openapi.TYPE_STRING, description="full name"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="password"),
            },
        ),
    )
    def post(self, request):
        """
        # check sms code
        """
        phone = request.data.get("phone", None)
        register = request.data.get("register", None)
        change_phone = request.data.get("change_phone", None)
        imei_code = request.data.get("imei_code", None)
        model_name = request.data.get("model_name", None)
        full_name = request.data.get("full_name", None)
        password = request.data.get("password", None)

        is_blocked = AuthService.is_user_blocked(phone=phone, type=CacheTypes.registration_sms_verification)
        if is_blocked:
            raise serializers.ValidationError("User is blocked", code="blocked_user")

        if phone:
            if register:
                if User.objects.filter(phone=phone).exists():
                    return Response(
                        {"status": "error", "message": "Бу номер тизимда мавжуд"}, status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    if OTP.check_code(phone, request.data["code"]):
                        with transaction.atomic():
                            user = User()
                            user.phone = phone
                            user.full_name = full_name
                            user.set_password(password)
                            user.save()

                            device = UserLoginDevice()
                            device.user = user
                            device.imei_code = imei_code
                            device.model_name = model_name
                            device.login_time = timezone.now()
                            device.save()

                            refresh = RefreshToken.for_user(user)
                            return Response(
                                {
                                    "status": "success",
                                    "message": "Мувофаққиятли рўйхатдан ўтилди",
                                    "refresh": str(refresh),
                                    "access": str(refresh.access_token),
                                },
                                status=status.HTTP_200_OK,
                            )
                    else:
                        return Response({"status": "error", "message": "Kod xato"}, status=status.HTTP_400_BAD_REQUEST)
            elif change_phone:
                if OTP.check_code(phone, request.data["code"]):
                    with transaction.atomic():
                        user = User.objects.get(pk=request.user.id)
                        user.phone = phone
                        user.save()

                        refresh = RefreshToken.for_user(user)
                        return Response(
                            {
                                "status": "success",
                                "message": "Телефон рақам мувофаққиятли ўзгартирилди",
                                "refresh": str(refresh),
                                "access": str(refresh.access_token),
                            },
                            status=status.HTTP_200_OK,
                        )
                else:
                    return Response({"status": "error", "message": "Kod xato"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if User.objects.filter(phone=phone).exists():
                    if OTP.check_code(phone, request.data["code"]):
                        user = User.objects.get(phone=phone)
                        user.last_login = timezone.now()
                        user.save()
                        refresh = RefreshToken.for_user(user)
                        if imei_code:
                            if UserLoginDevice.objects.filter(
                                    user=user, imei_code=imei_code, logged_out=False
                            ).exists():
                                device = UserLoginDevice.objects.get(user=user, imei_code=imei_code, logged_out=False)
                                device.login_time = timezone.now()
                                device.save()
                            else:
                                device = UserLoginDevice()
                                device.user = user
                                device.imei_code = imei_code
                                device.model_name = model_name
                                device.login_time = timezone.now()
                                device.save()
                        AuthService.reset_login_attempts(phone=phone, type=CacheTypes.registration_sms_verification)
                        return Response(
                            {"refresh": str(refresh), "access": str(refresh.access_token)}, status=status.HTTP_200_OK
                        )
                    else:
                        AuthService.check_login_attempts(phone=phone, type=CacheTypes.registration_sms_verification)
                        return Response({"status": "error", "message": "Kod xato"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    AuthService.check_login_attempts(phone=phone, type=CacheTypes.registration_sms_verification)
                    return Response(
                        {"status": "error", "message": "Bu raqam tizimda mavjud emas"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        else:
            AuthService.check_login_attempts(phone=phone, type=CacheTypes.registration_sms_verification)
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)


class CheckPhoneView(APIView):
    serializer_class = CheckPhoneSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone": openapi.Schema(type=openapi.TYPE_STRING, description="String with +"),
            },
        ),
    )
    def post(self, request):
        """
        # check phone number
        """
        phone = request.data.get("phone", None)
        if phone:
            if User.objects.filter(phone=phone).exists():
                return Response({"status": True}, status=status.HTTP_200_OK)
            else:
                return Response({"status": False}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": _("Телефон не указан"), "status": False}, status=status.HTTP_400_BAD_REQUEST)


class LogOutFromDeviceView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "imei_code": openapi.Schema(type=openapi.TYPE_STRING, description="String"),
            },
        ),
    )
    def post(self, request):
        """
        # logout from devices view
        """
        imei_code = request.data.get("imei_code", None)
        user = request.user
        if imei_code:
            device = UserLoginDevice.objects.get(imei_code=imei_code, user=user)
            device.logged_out = True
            device.logout_time = timezone.now()
            device.save()
        return Response({"status": True}, status=status.HTTP_200_OK)


class SendSmsCodeAPIView(APIView):
    """
    Send sms code to user

    types options:
    1. `forget_pass_verification`
    2. `registration_sms_verification`
    3. `login_sms_verification`
    4. `update_phone_verification`
    5. `change_password`
    6. `delete_profile`
    """

    queryset = OTP.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SendSmsCodeSerializer

    @swagger_auto_schema(
        tags=["Reset Password"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone": openapi.Schema(type=openapi.TYPE_STRING, description="String with +"),
                "type": openapi.Schema(type=openapi.TYPE_STRING, description="String"),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_type = serializer.validated_data["type"]
        phone = serializer.validated_data.get("phone", None)

        if request.user.is_authenticated:
            phone = request.user.phone
            user = request.user

        is_blocked = AuthService.is_user_blocked(phone=phone.as_e164, otp_type=otp_type)
        if is_blocked:
            raise serializers.ValidationError("User is blocked", code="blocked_user")


        sms = OTP.objects.filter(
            phone_number=phone,
            created_at__gte=(timezone.now() - datetime.timedelta(minutes=1)),
            sms_type=otp_type,
            is_verified=False,
            is_used=False,
        ).last()
        if sms:
            # Return how many seconds left to retry, if user has sent sms in last 1 minute
            time_to_retry = 60 - int((timezone.now() - sms.add_time).total_seconds())
            return Response({"sec_to_retry": time_to_retry}, status=status.HTTP_200_OK)

        otp = OTP.create_message(phone, otp_type=otp_type, ip=request.META["REMOTE_ADDR"])

        send_single_sms(otp)

        return Response({"sec_to_retry": 60, "session": otp.session}, status=status.HTTP_200_OK)


class VerifySMSCodeAPIView(APIView):
    """
    Verify sms code to user

    types options:
    1. `forget_pass_verification`
    2. `registration_sms_verification`
    3. `login_sms_verification`
    4. `update_phone_verification`
    5. `change_password`
    6. `delete_profile`
    """

    serializer_class = VerifySMSCodeSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=["Reset Password"], request_body=serializer_class)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = serializer.validated_data["session"]
        code = serializer.validated_data["code"]
        sms_type = serializer.validated_data["type"]
        phone = serializer.validated_data["phone"]

        is_blocked = AuthService.is_user_blocked(phone=phone.as_e164, otp_type=sms_type)
        if is_blocked:
            raise serializers.ValidationError("User is blocked", code="blocked_user")

        # check if sms code is valid
        OTP.check_code(phone, code, otp_type=sms_type, session=session)

        # if sms code is valid
        AuthService.reset_login_attempts(phone=phone.as_e164, type=sms_type)

        # return success
        return Response({"status": "success"}, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = serializer.validated_data["session"]
        password = serializer.validated_data["password"]

        short_msg = (
            OTP.objects.filter(
                sms_type=OTPTypes.FORGET_PASS_VERIFICATION.value,
                add_time__gte=(timezone.now() - datetime.timedelta(minutes=10)),
                session=session,
                is_code_verified=True,
                is_used=False,
            )
            .order_by("-add_time")
            .first()
        )

        if not short_msg:
            raise serializers.ValidationError(detail={"session": "Invalid session"}, code="invalid")

        # set OTP instance as used in database
        short_msg.is_used = True
        short_msg.save()

        # change user password
        user = User.objects.get(phone=short_msg.recipient)
        user.set_password(password)
        user.save()

        return Response({"status": "success"}, status=status.HTTP_200_OK)


class DeleteProfileAPIView(generics.DestroyAPIView):
    serializer_class = DeletedProfileSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(request_body=DeletedProfileSerializer, responses={204: openapi.Response("Success")})
    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.phone = f"deleted_{instance.id}__{instance.phone}"
        instance.save()
        return Response(data={"status": "success"}, status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(TokenObtainPairView):
    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
