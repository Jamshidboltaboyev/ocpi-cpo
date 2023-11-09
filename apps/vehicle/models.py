from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.accounts.models import User, Media
from apps.charge_point.models import Connector, InProgressTransaction

OPERATION = (
    (1, _("Hisob to'ldirildi")),
    (2, _("Hisob raqamidan pul yechib olindi")),
)


class Manufacturer(models.Model):
    name = models.CharField(_("Наименование"), max_length=30)
    icon = models.TextField(_("Значок"), null=True)
    user_defined = models.BooleanField(_("Добавлен пользователем"), default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Производитель")
        verbose_name_plural = _("Производители")


class VehicleModel(models.Model):
    name = models.CharField(_("Наименование"), max_length=100)
    manufacturer = models.ForeignKey(
        Manufacturer, related_name="car_models", verbose_name=_("Производитель"),
        on_delete=models.PROTECT, null=True, blank=True
    )
    user_defined = models.BooleanField(_("Добавлен пользователем"), default=False)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    VEHICLE_TYPES = ((1, _("car")),
                     (2, _("motorbike")))
    STATE_NUMBER_TYPES = ((1, _("Юридически лицо")),
                          (2, _("Физически лицо")),)

    user = models.ForeignKey(User, verbose_name=_("Пользователь"), on_delete=models.PROTECT)
    connector_type = models.ManyToManyField('charge_point.ConnectorType', verbose_name=_("Тип зарядки"))
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT)

    vin = models.CharField(_("VIN"), max_length=100, null=True)
    state_number = models.CharField(_("Гос.номер"), max_length=100, null=True, blank=True)
    type_state_number = models.IntegerField(_("Тип гос.номер"), choices=STATE_NUMBER_TYPES, null=True, blank=True)
    vehicle_type = models.IntegerField(_("Тип"), choices=VEHICLE_TYPES, default=1)
    usable_battery_size = models.FloatField(_("Полезный размер батареи"), default=0)
    release_year = models.CharField(_("Год выпуска"), max_length=100, null=True, blank=True)
    variant = models.CharField(_("Вариант"), max_length=100, null=True, blank=True)
    version = models.CharField(_("Версия"), max_length=15)
    is_deleted = models.BooleanField(_("Удален"), default=False)

    def __str__(self):
        return f"{self.user.phone}"


class Notification(models.Model):
    title = models.CharField(_("Заголовок"), max_length=256)
    message = models.TextField(_("Текст"))
    add_time = models.DateTimeField(_("Время"), auto_now_add=True)
    force_open = models.BooleanField(_("Majburiy ochish"), default=False)
    users = models.ManyToManyField(User, through="NotificationUser", related_name="notifications")

    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")

    def __str__(self):
        return self.title


class NotificationUser(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Пользователь"), on_delete=models.PROTECT)
    notification = models.ForeignKey(Notification, verbose_name=_("Уведомление"), on_delete=models.CASCADE)
    seen_time = models.DateTimeField(_("Видимый"), null=True, blank=True)

    class Meta:
        verbose_name = _("Пользователь уведомления")
        verbose_name_plural = _("Уведомления пользователей")


class News(models.Model):
    title = models.CharField(_("Заголовок"), max_length=256)
    message = models.TextField(_("Текст"))
    add_time = models.DateTimeField(_("Время"), auto_now_add=True)
    image = models.ForeignKey(Media, on_delete=models.PROTECT, verbose_name=_("Фото"), related_name="news")

    class Meta:
        verbose_name = _("Новости")
        verbose_name_plural = _("Новости")

    def __str__(self):
        return self.title


class Instruction(models.Model):
    title = models.CharField(_("Заголовок"), max_length=256)
    image = models.ForeignKey(
        to=Media, on_delete=models.PROTECT,
        verbose_name=_("Фото"), blank=True, null=True,
    )
    description = models.TextField(_("Описание"), null=True, blank=True)
    icon = models.TextField(_("Значок"), null=True)

    class Meta:
        verbose_name = _("Инструкция")
        verbose_name_plural = _("Инструкции")

    def __str__(self):
        return self.title


class Appeal(models.Model):
    title = models.TextField(_("текст"))

    class Meta:
        verbose_name = _("Обращение")
        verbose_name_plural = _("Обращения")

    def __str__(self):
        return self.title


class About(models.Model):
    title = models.CharField(_("Заголовок"), max_length=256)
    description = models.TextField(_("Текст"))
    phone = models.CharField(_("Телефон"), max_length=256)
    email = models.CharField(_("Email"), max_length=256)
    bot_username = models.CharField(_("Telegram bot"), max_length=256)
    created_at = models.DateTimeField(_("Vaqt"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Vaqt"), auto_now=True)

    class Meta:
        verbose_name = _("О нас")
        verbose_name_plural = _("О нас")

    def __str__(self):
        return self.title
