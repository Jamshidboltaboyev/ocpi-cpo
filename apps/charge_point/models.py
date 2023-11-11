from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.accounts.models import User


class Country(models.Model):
    name = models.CharField(_("Наименование"), max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Страна")
        verbose_name_plural = _("Страны")


class Region(models.Model):
    name = models.CharField(_("Наименование"), max_length=25)
    country = models.ForeignKey(Country, verbose_name=_("Страна"), related_name="regions", on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Регион")
        verbose_name_plural = _("Регионы")


class Address(models.Model):
    region = models.ForeignKey(Region, verbose_name=_("Регион"), related_name="address", on_delete=models.PROTECT)
    name = models.CharField(_("Наименование"), max_length=50)
    address = models.CharField(_("Адрес"), max_length=100)
    landmark = models.CharField(_("Ориентир"), max_length=100, null=True)
    longitude = models.DecimalField(_("Длина"), max_digits=9, decimal_places=6, null=True, blank=True)
    latitude = models.DecimalField(_("Широта"), max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Адрес")
        verbose_name_plural = _("Адреса")


class PowerUnit(models.Model):
    name = models.CharField(_("Наименование"), max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Единица измерения")
        verbose_name_plural = _("Единица измерении")


class PowerGroup(models.Model):
    count = models.FloatField(_("Количество"))
    unit = models.ForeignKey(PowerUnit, verbose_name=_("Ед.изм"), related_name="power_group", on_delete=models.PROTECT)

    def __str__(self):
        return str(self.count) + self.unit.name

    class Meta:
        verbose_name = _("Группа мощность")
        verbose_name_plural = _("Группы мощносты")


class ConnectorType(models.Model):
    class Type(models.TextChoices):
        AC = 'AC'
        DC = 'DC'

    name = models.CharField(_("Наименование"), max_length=40)
    count_amper = models.CharField(_("Количество тока"), max_length=50, null=True)
    count_phase = models.CharField(_("Количество фаза"), max_length=50, null=True)
    type = models.CharField(max_length=10, choices=Type.choices)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тип соединения")
        verbose_name_plural = _("Типы соединения")


class ChargePoint(models.Model):
    name = models.CharField(_("Названия"), max_length=128)
    model = models.CharField(_("Модель"), max_length=128)
    vendor = models.CharField(_("Производитель"), max_length=128)
    serial_number = models.CharField(_("Серия"), max_length=25, null=True, blank=True)
    firmware = models.CharField(_("Прошивка"), max_length=50, null=True, blank=True)
    type = models.CharField(_("Тип"), max_length=25, null=True, blank=True)
    last_heartbeat = models.DateTimeField(_("Последняя подключения"), null=True, blank=True)
    boot_timestamp = models.DateTimeField(_("Время загрузки"), null=True, blank=True)
    identity = models.CharField(_("Идентификация"), max_length=50)
    connected = models.BooleanField(_("Подключен"), default=False)
    status = models.BooleanField(_("Активный"), default=False)
    address = models.ForeignKey(Address, verbose_name=_("Адрес"), on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.identity}"

    class Meta:
        verbose_name = _("Станция")
        verbose_name_plural = _("Станции")
        ordering = ["id"]


class Price(models.Model):
    PRICE_TYPES = (
        (1, _("Sum/kWh")),
        (2, _("Sum/hour")),
        (2, _("Locking/min")),
    )
    price_type = models.IntegerField(_("Тип"), choices=PRICE_TYPES, default=1)
    price = models.IntegerField(_("Цена"))
    start_date = models.DateTimeField(_("Время начало"), null=True, blank=True)
    end_date = models.DateTimeField(_("Время окончания"), null=True, blank=True)

    def __str__(self):
        return str(self.price)

    class Meta:
        verbose_name = _("Цена")
        verbose_name_plural = _("Цены")


class Connector(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "Available"
        PREPARING = "Preparing"
        CHARGING = "Charging"
        SUSPENDED_EVSE = "SuspendedEVSE"
        SUSPENDED_EV = "SuspendedEV"
        FINISHING = "Finishing"
        RESERVED = "Reserved"
        UNAVAILABLE = "Unavailable"
        FAULTED = "Faulted"

    name = models.CharField(_("Наименование"), max_length=40, null=True)
    connector_id = models.IntegerField(_("№ коннектора"))
    charge_point = models.ForeignKey(ChargePoint, on_delete=models.PROTECT, related_name="connectors")
    available = models.BooleanField(_("Доступен?"), default=False)
    in_use = models.BooleanField(_("Занят?"), default=False)
    status = models.CharField(_("Статус"), choices=Status.choices, max_length=50, default=Status.UNAVAILABLE)
    power = models.ForeignKey(PowerGroup, verbose_name=_("Группы мощность"), on_delete=models.PROTECT)
    connector_type = models.ForeignKey(ConnectorType, verbose_name=_("Тип соединения"), on_delete=models.PROTECT)
    icon = models.TextField(_("Значок"), null=True)

    price_for_charge = models.ForeignKey(
        Price, verbose_name=_("Цена зарядки"), on_delete=models.PROTECT, related_name="for_change"
    )
    price_for_wait = models.ForeignKey(
        Price, verbose_name=_("Цена ожидания"), on_delete=models.PROTECT, related_name="for_wait"
    )
    price_for_parking = models.ForeignKey(
        Price, verbose_name=_("Цена парковки"), on_delete=models.PROTECT, related_name="for_parking"
    )

    class Meta:
        unique_together = ("charge_point_id", "connector_id")
        verbose_name = _("Коннектор")
        verbose_name_plural = _("Коннекторы")
        ordering = ["id"]

    def __str__(self):
        return f"{self.charge_point}: № {self.connector_id}"


class ChargePointError(models.Model):
    connector_id = models.ForeignKey(
        Connector, verbose_name=_("Коннектор"), on_delete=models.PROTECT, related_name="errors"
    )
    error_code = models.CharField(_("Код ошибки"), max_length=50, null=True)
    info = models.CharField(_("Info"), max_length=50, null=True)
    status = models.CharField(_("Status"), max_length=50, null=True)
    timestamp = models.DateTimeField(_("Время"))
    vendor_id = models.CharField(_("Вендор"), max_length=255, null=True)
    vendor_error_code = models.CharField(_("Код ошибки вендора"), max_length=50, null=True, blank=True)


class TokenGroup(models.Model):  # todo ask
    token = models.CharField(_("Token"), max_length=20)


class Token(models.Model):  # todo ask
    token = models.CharField(_("Token"), max_length=20)
    token_group = models.ForeignKey(TokenGroup, related_name="tokens", on_delete=models.PROTECT)


class ChargeTransaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="charge_transactions", null=True, blank=True
    )
    reservation_id = models.IntegerField(null=True, blank=True)
    start_timestamp = models.DateTimeField(_("Время начала"))
    end_timestamp = models.DateTimeField(_("Время окончания"))
    duration = models.DurationField(_("Длительность"))
    meter_start = models.IntegerField(_("Начало счетчика"))
    meter_stop = models.IntegerField(_("Конец счетчика"))
    meter_used = models.IntegerField(_("Использовано"))
    stop_reason = models.TextField(_("Причина остановки"), null=True, blank=True)
    connector = models.ForeignKey(Connector, verbose_name=_("Коннектор"), on_delete=models.PROTECT)
    start_token = models.ForeignKey(
        Token, on_delete=models.PROTECT, related_name="start_transactions", null=True, blank=True
    )
    end_token = models.ForeignKey(
        Token, on_delete=models.PROTECT, related_name="end_transactions", null=True, blank=True
    )
    cost = models.BigIntegerField(_("Сумма"), default=0)
    vehicle = models.ForeignKey('vehicle.Vehicle', on_delete=models.PROTECT, related_name="transactions")
    sent = models.BooleanField(_("Отправлено"), default=False)

    class Meta:
        verbose_name = _("Транзакция зарядки")
        verbose_name_plural = _("Транзакции зарядки")

    def __str__(self):
        return str(self.pk)


class InProgressTransaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="in_progress_transactions", null=True, blank=True
    )
    start_timestamp = models.DateTimeField(_("Время начала"))
    meter_start = models.IntegerField(_("Начало счетчика"))
    reservation_id = models.IntegerField(null=True, blank=True)
    connector = models.ForeignKey(
        Connector, verbose_name=_("Коннектор"), on_delete=models.PROTECT, related_name="in_progress_transactions"
    )

    start_token = models.ForeignKey(
        Token, on_delete=models.PROTECT, related_name="starting_transactions", null=True, blank=True
    )

    current = models.FloatField(_("Ток"), default=0.0)  # Current.Import A.
    energy = models.FloatField(_("Энергия"), default=0.0)  # Energy.Active.Import.Register Wh
    power = models.FloatField(_("Мощность"), default=0.0)  # Power.Active.Import W
    soc = models.SmallIntegerField(_("Текущий %"), default=0)  # SoC %
    voltage = models.FloatField(_("Напряжения"), default=0.0)  # Voltage V
    end = models.BooleanField(_("Закончен"), default=False)

    class Meta:
        verbose_name = _("Не законченная транзакция")
        verbose_name_plural = _("Не законченные транзакции")


class AuthorizationRequest(models.Model):
    charge_point = models.ForeignKey(ChargePoint, verbose_name=_("Станция"), on_delete=models.PROTECT)
    token = models.ForeignKey(Token, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(_("Время"))

    class Meta:
        verbose_name = _("Запрос на авторизация")
        verbose_name_plural = _("Запросы на авторизация")


class PriceChargePointConnector(models.Model):
    PRICE_TYPES = (
        (1, _("Sum/kWh")),
        (2, _("Sum/hour")),
        (2, _("Locking/min")),
    )
    price_type = models.IntegerField(_("Тип"), choices=PRICE_TYPES, default=1)
    price = models.CharField(_("Цена"), max_length=20)
    start_date = models.DateTimeField(_("Время начало"), null=True, blank=True)
    end_date = models.DateTimeField(_("Время окончания"), null=True, blank=True)
    connector = models.ForeignKey(Connector, verbose_name=_("Коннектор"), on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.connector.connector_id} + {self.price}"

    class Meta:
        verbose_name = _("Цена коннектор")
        verbose_name_plural = _("Цены коннектор")


class CommentsChargePoint(models.Model):
    created_at = models.DateTimeField(_("Время"), editable=False)
    charger_point = models.ForeignKey(ChargePoint, verbose_name=_("Станция"), on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=_("Пользователь"), on_delete=models.PROTECT)
    content = models.TextField(_("Текст"))
    deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.created_date = timezone.now()
        return super(CommentsChargePoint, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Комментарий")
        verbose_name_plural = _("Комментарии")

    def __str__(self):
        return self.content


class FavoriteChargePoint(models.Model):
    charger_point = models.ForeignKey(
        ChargePoint, verbose_name=_("Станция"), related_name="user_favorites", on_delete=models.PROTECT
    )
    user = models.ForeignKey(
        User, verbose_name=_("Пользователь"), on_delete=models.PROTECT, related_name="user_favorites"
    )

    class Meta:
        verbose_name = _("Избранные")
        verbose_name_plural = _("Избранные")
        unique_together = (("charger_point", "user"),)

    def __str__(self):
        return self.charger_point.model


class FavoriteAddress(models.Model):
    address = models.ForeignKey(
        Address, verbose_name=_("Адрес"), related_name="user_favorites", on_delete=models.PROTECT
    )
    user = models.ForeignKey(
        User, verbose_name=_("Пользователь"), on_delete=models.PROTECT, related_name="user_favorites_address"
    )

    class Meta:
        verbose_name = _("Избранные адреса")
        verbose_name_plural = _("Избранные адреса")
        unique_together = (("address", "user"),)

    def __str__(self):
        return self.address.name


class ChargePointTask(models.Model):
    TASK_TYPES = (
        ("ReserveNow", "ReserveNow"),
        ("CancelReservation", "CancelReservation"),
        ("ChangeAvailability", "ChangeAvailability"),
        ("RemoteStartTransaction", "RemoteStartTransaction"),
        ("RemoteStopTransaction", "RemoteStopTransaction"),
        ("UnlockConnector", "UnlockConnector"),
    )
    # charge_point = models.ForeignKey(ChargePoint, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="tasks")
    task_type = models.CharField(_("Tip"), choices=TASK_TYPES, max_length=32)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    response_text = models.CharField(_("Javob"), max_length=1024, null=True, blank=True)
    running = models.BooleanField(_("Olindi"), default=False)
    done = models.BooleanField(_("Tugadi"), default=False)
    vehicle = models.ForeignKey('vehicle.Vehicle', on_delete=models.PROTECT, related_name="charge_tasks", null=True)
    transaction = models.OneToOneField(
        InProgressTransaction, on_delete=models.PROTECT, related_name="task", null=True, blank=True
    )

    created_at = models.DateTimeField(_("Vaqt"), auto_now_add=True)
