from datetime import datetime
import string
import phonenumbers
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .cache import CacheTypes
from .helpers import send_single_sms
from .models import User, Otp, UserLoginDevice
from .serializers import (ActivateSerializer, CheckPhoneSerializer,
                                  DeletedProfileSerializer,
                                  DeleteImageSerializer, LogoutSerializer,
                                  SendSmsCodeSerializer,
                                  UploadedImageSerializer, UserSerializer, ForgotPasswordSerializer)
from core.models import UploadedImage
from utils.user_auth import AuthService


class UploadedImageCreateView(generics.CreateAPIView):
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer
    parser_classes = (MultiPartParser,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exteption=True):
            uploaded_image = serializer.save()
            return Response({"id": uploaded_image.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            image = UploadedImage.objects.get(pk=avatar_id)
            image.delete()

            return Response({"status": "image o'chirildi"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "ushbu id da rasm topilmadi"}, status=status.HTTP_400_BAD_REQUEST)


class AccountView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    allowed_method = ["GET", "POST"]
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=["Account"], operation_summary="Get Current User")
    def get(self, request):
        serializer = UserSerializer(request.user, read_only=True)
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
        full_name = request.data.get('full_name', None)
        birth_date = request.data.get('birth_date', None)
        avatar_id = request.data.get('avatar_id', None)

        if full_name is not None and birth_date is not None:

            if avatar_id == 0:

                birth_date = datetime.strptime(birth_date, "%d.%m.%Y").strftime("%Y-%m-%d")
                user = self.queryset.get(pk=request.user.id)
                user.full_name = full_name
                user.birth_date = birth_date
                user.birth_date_editable = False
                user.avatar = None
                user.save()

            elif avatar_id is not None and avatar_id != 0:
                if UploadedImage.objects.filter(pk=avatar_id).exists():
                    birth_date = datetime.strptime(birth_date, "%d.%m.%Y").strftime("%Y-%m-%d")
                    user = self.queryset.get(pk=request.user.id)
                    user.full_name = full_name
                    user.birth_date = birth_date
                    user.birth_date_editable = False
                    user.avatar_id = avatar_id
                    user.save()
                else:
                    return Response(
                        {"status": "error", "message": "Rasm topilmadi"}, status=status.HTTP_400_BAD_REQUEST
                    )

            if "phone" in request.data:
                try:
                    phone = phonenumbers.parse(request.data["phone"])
                except Exception as _:
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
                            code = get_random_string(6, allowed_chars=string.digits)
                            session = get_random_string(10, string.printable)

                            text = "UIC Tasdiqlash kodi {}".format(code)
                            sm = Otp.create_message(
                                request.data["phone"], text, user, code, request.META["REMOTE_ADDR"], session
                            )
                            # todo send_single_sms(sm)

                    return Response(
                        {"status": "success", "data": UserSerializer(user).data, "send_code": changed_phone},
                        status=status.HTTP_200_OK,
                    )
            else:
                return Response({"status": "success", "data": UserSerializer(user).data}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    queryset = Otp.objects.all()
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
        phone = request.data.get("phone", "")

        if AuthService.is_user_blocked(phone=phone, type=CacheTypes.registration_sms_verification):
            raise serializers.ValidationError("User is blocked", code="blocked_user")

        try:
            parsed_phone = phonenumbers.parse(phone)
        except phonenumbers.phonenumberutil.NumberParseException:
            return Response({"status": "error", "message": "Нотўғри номер"}, status=status.HTTP_400_BAD_REQUEST)

        if not phonenumbers.is_possible_number(parsed_phone):
            return Response({"status": "error", "message": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None

        if User.objects.filter(phone=phone).exists():
            return Response(
                {"status": "error", "message": "Бу рақам тизимда мавжуд"},
                status=status.HTTP_400_BAD_REQUEST)

        sms = Otp.objects.filter(recipient=phone,
                                          add_time__gte=(timezone.now() - datetime.timedelta(minutes=1))).last()
        if sms:
            time_to_retry = 60 - int((timezone.now() - sms.add_time).total_seconds())
            return Response({"sec_to_retry": time_to_retry}, status=status.HTTP_200_OK)

        code: str = get_random_string(6, allowed_chars=string.digits)
        session = get_random_string(10, string.printable)

        text = "UIC Tasdiqlash kodi {}".format(code)

        sm = Otp.create_message(phone, text, user, code, request.META.get("REMOTE_ADDR"), session)
        # todo send_single_sms(sm)
        return Response({"sec_to_retry": 60}, status=status.HTTP_200_OK)


class ActivateView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ActivateSerializer

    @swagger_auto_schema(
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
        )
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
                    if Otp.check_code(phone, request.data["code"]):
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
                if Otp.check_code(phone, request.data["code"]):
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
                    if Otp.check_code(phone, request.data["code"]):
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


class CheckPhoneView(generics.CreateAPIView):
    serializer_class = CheckPhoneSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        exists = User.objects.filter(phone=phone).exists()
        return Response({"status": exists}, status=status.HTTP_200_OK)


class LogOutFromDeviceView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "imei_code": openapi.Schema(type=openapi.TYPE_STRING, description="String"),
            },
        )
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


class SendSmsCodeView(generics.CreateAPIView):
    """
    Send SMS code to the user

    types options:
    1. `forget_pass_verification`
    2. `registration_sms_verification`
    3. `login_sms_verification`
    4. `update_phone_verification`
    5. `change_password`
    6. `delete_profile`
    """

    queryset = Otp.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SendSmsCodeSerializer

    @swagger_auto_schema(request_body=SendSmsCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        type_ = serializer.validated_data['type']
        phone = serializer.validated_data['phone']

        if AuthService.is_user_blocked(phone=phone, type_=type_):
            raise serializers.ValidationError("User is blocked", code="blocked_user")

        last_sms = Otp.objects.filter(
            recipient=phone,
            add_time__gte=(timezone.now() - datetime.timedelta(minutes=1))
        ).last()

        if last_sms:
            time_to_retry = 60 - (timezone.now() - last_sms.add_time).total_seconds()
            return Response({"sec_to_retry": time_to_retry}, status=status.HTTP_200_OK)

        code = get_random_string(6, allowed_chars=string.digits)
        session = get_random_string(10, string.printable)

        text = f"UIC Tasdiqlash kodi {code}"
        user = request.user if request.user.is_authenticated else None
        sm = Otp.create_message(phone, text, user, code, request.META["REMOTE_ADDR"], session)
        # todo send_single_sms(sm)
        return Response({"sec_to_retry": 60}, status=status.HTTP_200_OK)


class DeleteProfileApiView(generics.DestroyAPIView):
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
        return Response(status=status.HTTP_204_NO_CONTENT)


class ForgotPasswrdAPIView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer
    queryset = Otp.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = get_random_string(5, string.digits)
        session = get_random_string(10, string.printable)
        text = f"Tasqidlash kodi: {code}"
        sm = Otp.create_message(
            serializer.validated_data['phone'], text, code, request.META["REMOTE_ADDR"], session)
        # todo send_single_sms(sm)
        return Response(data={"session": sm.session})
