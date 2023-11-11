import datetime
from typing import List

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.exceptions import ValidationError

from .cache import OTPTypes
# from .helpers
# from utils.user_auth import AuthService

from .managers import UserManager, PermissionsMixin

USER_TYPES = (
    (1, "client"),
    (2, "operator"),
    (3, "admin"),
)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    father_name = models.CharField(max_length=150, null=True, blank=True)
    user_type = models.SmallIntegerField(choices=USER_TYPES, default=1)
    full_name = models.CharField(max_length=150, null=True, blank=True)
    birth_date = models.DateField(null=True)
    free_charging_time = models.IntegerField(null=True, blank=True)
    free_charging_to_date = models.DateField(null=True, blank=True)
    phone = PhoneNumberField(unique=True)
    amount = models.FloatField(_("shaxsiy hisob"), default=0)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True)
    avatar = models.ForeignKey(
        "Media", on_delete=models.PROTECT, verbose_name=_("Rasm"), null=True, related_name="user_image"
    )
    birth_date_editable = models.BooleanField(default=True)
    is_deleted = models.BooleanField(verbose_name=_("Is deleted"), default=False)
    deleted_at = models.DateTimeField(verbose_name=_("Deleted at"), null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS: List[str] = []

    def __str__(self):
        return str(self.phone)

    def get_full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''} {self.father_name or ''}"

    def get_short_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}"


class Otp(models.Model):
    recipient = models.CharField(_("Qabul qiluvchi"), max_length=13)  # +998991234567
    message_id = models.CharField(_("Broker SMS ID"), max_length=20, unique=True, editable=False, blank=True, null=True)
    text = models.CharField(_("Matn"), max_length=160)
    code = models.CharField(_("Kod"), max_length=20, null=True)
    sent = models.BooleanField(_("Jo'natildi"), default=False)
    add_time = models.DateTimeField(_("Qo'shilgan vaqti"), auto_now_add=True)
    sent_time = models.DateTimeField(_("Jo'natilgan vaqti"), null=True, blank=True)
    ip = models.CharField(_("Foydalanuvchi IP manzili"), max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = _("SMS")
        verbose_name_plural = _("SMSlar")

    def __str__(self):
        return self.message_id

    def save(self, *args, **kwargs):
        if not self.message_id:
            if not self.id:
                latest = Otp.objects.order_by("id").last()
                if latest:
                    _id = latest.id + 1
                else:
                    _id = 1
            else:
                _id = self.id
            self.message_id = "ZTY{0:017d}".format(_id)
        super(Otp, self).save(*args, **kwargs)

    @staticmethod
    def check_code(phone, code, sender=None, type_: str = OTPTypes.REGISTRATION_SMS_VERIFICATION):
        if code is None or phone is None:
            AuthService.check_login_attempts(phone=phone, type=type_)
            raise ValidationError("invalid_code")

        code = code.strip()

        query = Otp.objects.filter(
            recipient=phone, add_time__gte=(timezone.now() - datetime.timedelta(minutes=1))
        )

        if sender:
            query = query.filter(sender=sender)

        last_sms = query.order_by("add_time").last()
        if not last_sms:
            AuthService.check_login_attempts(phone=phone, type=type_)
            raise ValidationError("invalid_code")

        if last_sms.code != code:
            AuthService.check_login_attempts(phone=phone, type=type_)
            raise ValidationError("invalid_code")

        return True

    @staticmethod
    def is_spam(sender, ip, phone):
        spam_query = (
            Otp.objects.filter(add_time__date=timezone.now().date())
            .exclude(recipient=phone)
            .values("recipient")
            .distinct()
        )
        if sender and sender.is_authenticated:
            if spam_query.filter(sender=sender).count() > 3:
                return True
        elif ip:
            if spam_query.filter(ip=ip).count() > 3:
                return True
        return False

    @staticmethod
    def create_message(phone, message, sender=None, code=None, ip=None, session: str = ""):
        if phone in ['+998901231212', '+998712007007', "+998996488450"]:
            code: str = "081020"

        sms = Otp.objects.create(
            sender=sender, recipient=phone, text=message, code=code, ip=ip, session=session)
        return sms


class UserLoginDevice(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("Фойдаланувчи"), null=True, related_name="devices"
    )
    model_name = models.CharField(_("Қурилма номи"), max_length=50, null=True, blank=True)
    imei_code = models.CharField(_("IMEI"), max_length=50, null=True, blank=True)
    login_time = models.DateTimeField(_("Тизимга кирган санаси"), null=True, blank=True)
    logged_out = models.BooleanField(default=False, blank=True)
    logout_time = models.DateTimeField(_("Тизимдан чиқиш санаси"), null=True, blank=True)

    class Meta:
        verbose_name = _("Фойдаланувчи қурилмаси")
        verbose_name_plural = _("Фойдаланувчи қурилмалари")
        unique_together = ("user", "imei_code")

    def __str__(self):
        return self.imei_code


class QrCodeScanerCount(models.Model):
    count = models.IntegerField(_("Сканлаган QR кодлар сони"), null=True, blank=True)
    iphone = models.IntegerField(_("Iphone"), null=True, blank=True)
    android = models.IntegerField(_("Android"), null=True, blank=True)
    last_scan = models.DateTimeField(_("Сканлаган сана"), auto_now_add=True)

    class Meta:
        verbose_name = _("QR кодлар сони")
        verbose_name_plural = _("QR кодлар сони")

    def __str__(self):
        return str(self.count)


class UserGift(models.Model):
    class GiftStatus(models.TextChoices):
        ACTIVE = "active", _("Актив")
        USED = "used", _("Фойдаланган")
        EXPIRED = "expired", _("Муддати ўтган")

    user = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("Фойдаланувчи"), null=True, related_name="gifts"
    )
    status = models.CharField(_("Статус"), max_length=10, choices=GiftStatus.choices, default=GiftStatus.ACTIVE)
    expired_date = models.DateTimeField(_("Муддати"), null=True, blank=True)

    class Meta:
        verbose_name = _("Фойдаланувчи совгаси")
        verbose_name_plural = _("Фойдаланувчи совгалари")

    def __str__(self):
        return str(self.user)


class DeletedAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = PhoneNumberField(_("Телефон рақами"), null=True, blank=True)
    first_name = models.CharField(_("Исм"), max_length=255, null=True, blank=True)
    last_name = models.CharField(_("Фамилия"), max_length=255, null=True, blank=True)
    reason = models.CharField(_("Сабаби"), max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _("Deleted account")
        verbose_name_plural = _("Deleted accounts")


class Media(models.Model):
    image = models.ImageField(_("Фото"), upload_to="%Y/%m/%d")

    class Meta:
        verbose_name = _("Фото")
        verbose_name_plural = _("Фото")

    def __str__(self):
        return self.image.name
