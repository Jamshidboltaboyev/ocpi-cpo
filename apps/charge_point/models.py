from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from apps.core.models import TimeStampedModel
from apps.accounts.models import User


class Country(TimeStampedModel):
    ico_code = models.CharField(max_length=10, verbose_name=_("ISO code"))
    name = models.CharField(max_length=30, verbose_name=_(_("Name")))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")


class Region(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=255)
    country = models.ForeignKey(Country, verbose_name=_("Country"), on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']
        verbose_name = _("Region")
        verbose_name_plural = _("Region")


class District(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=25)
    country = models.ForeignKey(to=Region, verbose_name=_("Region"), on_delete=models.PROTECT)


class PublishTokenType(TimeStampedModel):
    class WhitelistType(models.TextChoices):
        ALWAYS = "ALWAYS"
        ALLOWED = "ALLOWED"
        ALLOWED_OFFLINE = "ALLOWED_OFFLINE"
        NEVER = "NEVER"

    uid = models.CharField(max_length=36, verbose_name=_("Uid"), null=True, blank=True)
    type = models.CharField(max_length=50, choices=WhitelistType.choices, verbose_name=_("White List Type"))


class Location(TimeStampedModel):
    class ParkingType(models.TextChoices):
        UNDERGROUND_GARAGE = 'UNDERGROUND_GARAGE'
        ON_STREET = 'ON_STREET'
        ON_DRIVEWAY = 'ON_DRIVEWAY'
        PARKING_LOT = 'PARKING_LOT'
        PARKING_GARAGE = 'PARKING_GARAGE'
        ALONG_MOTORWAY = 'ALONG_MOTORWAY'

    district = models.ForeignKey(to=District, on_delete=models.PROTECT, verbose_name=_("District"))
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    address = models.CharField(max_length=100, verbose_name=_("Address"))
    landmark = models.CharField(max_length=100, null=True, verbose_name=_("Landmark"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_("Longitude"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_("Latitude"))
    parking_type = models.CharField(max_length=50, choices=ParkingType.choices, verbose_name=_("Parking Type"))
    publish = models.BooleanField(default=True, verbose_name=_("Allowed to all MSPs"))
    publish_allowed_to = models.ManyToManyField(to=PublishTokenType, blank=True, verbose_name=_("Allowed MSPs Tokens"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")


class ChargePoint(TimeStampedModel):
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE'
        BLOCKED = "BLOCKED"
        CHARGING = 'CHARGING'
        INOPERATIV = 'INOPERATIVE'
        OUTOFORDER = "OUTOFORDER"
        PLANNED = "PLANNED"
        REMOVED = "REMOVED"
        RESERVED = "RESERVED"
        UNKNOWN = "UNKNOWN"

    location = models.ForeignKey(to=Location, on_delete=models.PROTECT, verbose_name=_("Location"))
    identity = models.CharField(max_length=50, verbose_name=_("Identity"))
    boot_timestamp = models.DateTimeField(verbose_name=_("Boot timestamp"), null=True, blank=True)
    model = models.CharField(max_length=128, verbose_name=_("Charge point model"), null=True, blank=True)
    vendor = models.CharField(max_length=128, verbose_name=_("Charge point vendor"), null=True, blank=True)
    serial_number = models.CharField(max_length=25, verbose_name=_("Charge point serial number"), null=True, blank=True)
    firmware = models.CharField(max_length=50, verbose_name=_("Firmware Version"), null=True, blank=True)
    last_heartbeat = models.DateTimeField(verbose_name="Last Heartbeat", null=True, blank=True)
    is_connected = models.BooleanField(default=False, verbose_name=_("is Connected"))
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=50, choices=Status.choices)

    name = models.CharField(max_length=128, verbose_name=_("Name"))

    def __str__(self):
        return f"{self.name} - {self.identity}"

    class Meta:
        verbose_name = _("ChargePoint")
        verbose_name_plural = _("ChargePoints")
        ordering = ["-id"]


class ConnectorType(TimeStampedModel):
    pass


class Connector(TimeStampedModel):
    class ConnectorType(models.TextChoices):
        CHADEMO = 'CHADEMO'
        CHAOJI = 'CHAOJI'
        DOMESTIC_A = 'DOMESTIC_A'
        DOMESTIC_B = 'DOMESTIC_B'
        DOMESTIC_C = 'DOMESTIC_C'
        DOMESTIC_D = 'DOMESTIC_D'
        DOMESTIC_E = 'DOMESTIC_E'
        DOMESTIC_F = 'DOMESTIC_F'
        DOMESTIC_G = 'DOMESTIC_G'
        DOMESTIC_H = 'DOMESTIC_H'
        DOMESTIC_I = 'DOMESTIC_I'
        DOMESTIC_J = 'DOMESTIC_J'
        DOMESTIC_K = 'DOMESTIC_K'
        DOMESTIC_L = 'DOMESTIC_L'
        DOMESTIC_M = 'DOMESTIC_M'
        DOMESTIC_N = 'DOMESTIC_N'
        DOMESTIC_O = 'DOMESTIC_O'
        GBT_AC = 'GBT_AC'
        GBT_DC = 'GBT_DC'
        IEC_60309_2_SINGLE_16 = 'IEC_60309_2_single_16'
        IEC_60309_2_THREE_16 = 'IEC_60309_2_three_16'
        IEC_60309_2_THREE_32 = 'IEC_60309_2_three_32'
        IEC_60309_2_THREE_64 = 'IEC_60309_2_three_64'
        IEC_62196_T1 = 'IEC_62196_T1'
        IEC_62196_T1_COMBO = 'IEC_62196_T1_COMBO'
        IEC_62196_T2 = 'IEC_62196_T2'
        IEC_62196_T2_COMBO = 'IEC_62196_T2_COMBO'
        IEC_62196_T3A = 'IEC_62196_T3A'
        IEC_62196_T3C = 'IEC_62196_T3C'
        NEMA_5_20 = 'NEMA_5_20'
        NEMA_6_30 = 'NEMA_6_30'
        NEMA_6_50 = 'NEMA_6_50'
        NEMA_10_30 = 'NEMA_10_30'
        NEMA_10_50 = 'NEMA_10_50'
        NEMA_14_30 = 'NEMA_14_30'
        NEMA_14_50 = 'NEMA_14_50'
        PANTOGRAPH_BOTTOM_UP = 'PANTOGRAPH_BOTTOM_UP'
        PANTOGRAPH_TOP_DOWN = 'PANTOGRAPH_TOP_DOWN'
        TESLA_R = 'TESLA_R'
        TESLA_S = 'TESLA_S'

    class ConnectorFormat(models.TextChoices):
        SOCKET = 'SOCKET'
        CABLE = 'CABLE'

    class PowerType(models.TextChoices):
        AC_1_PHASE = 'AC_1_PHASE'  # 'AC single phase.'
        AC_2_PHASE = 'AC_2_PHASE'  # 'AC two phases, only two of the three available phases connected.'
        AC_2_PHASE_SPLIT = 'AC_2_PHASE_SPLIT'  # '3 AC two phases using split phase system.'
        AC_3_PHASE = 'AC_3_PHASE'  # 'AC three phases.'
        DC = 'DC'  # 'Direct Current.'

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

    charge_point = models.ForeignKey(ChargePoint, on_delete=models.PROTECT)
    name = models.CharField(_("Наименование"), max_length=40, null=True)

    connector_id = models.IntegerField(verbose_name=_("Connector Id within EVS"))
    standard = models.CharField(max_length=50, choices=ConnectorType.choices, verbose_name=_("Connector's standard"))
    format = models.CharField(max_length=50, choices=ConnectorFormat.choices, verbose_name=_("Connector's format"))
    power_type = models.CharField(max_length=50, choices=PowerType.choices, verbose_name=_("Connector's power type"))
    max_voltage = models.IntegerField(default=0, verbose_name=_("Connector's Max Voltage"))
    max_amperage = models.IntegerField(default=0, verbose_name=_("Connector's Max Amperage"))
    max_electric_power = models.IntegerField(default=0, verbose_name=_("Connector's Max electric power"))

    status = models.CharField(_("Статус"), choices=Status.choices, max_length=50, default=Status.UNAVAILABLE)

    price_for_charge = models.DecimalField(max_digits=10, decimal_places=2)
    price_for_wait = models.DecimalField(max_digits=10, decimal_places=2)
    price_for_parking = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("charge_point_id", "connector_id")
        verbose_name = _("Коннектор")
        verbose_name_plural = _("Коннекторы")
        ordering = ["id"]

    def __str__(self):
        return f"{self.charge_point}: № {self.connector_id}"


class ChargePointError(TimeStampedModel):
    connector_id = models.ForeignKey(
        Connector, verbose_name=_("Коннектор"), on_delete=models.PROTECT, related_name="errors"
    )
    error_code = models.CharField(_("Код ошибки"), max_length=50, null=True)
    info = models.CharField(_("Info"), max_length=50, null=True)
    status = models.CharField(_("Status"), max_length=50, null=True)
    timestamp = models.DateTimeField(_("Время"))
    vendor_id = models.CharField(_("Вендор"), max_length=255, null=True)
    vendor_error_code = models.CharField(_("Код ошибки вендора"), max_length=50, null=True, blank=True)


class TokenGroup(TimeStampedModel):  # todo ask
    token = models.CharField(_("Token"), max_length=20)


class Token(TimeStampedModel):  # todo ask
    token = models.CharField(_("Token"), max_length=20)
    token_group = models.ForeignKey(TokenGroup, related_name="tokens", on_delete=models.PROTECT)


class ChargeTransaction(TimeStampedModel):
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


class InProgressTransaction(TimeStampedModel):
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


class AuthorizationRequest(TimeStampedModel):
    charge_point = models.ForeignKey(ChargePoint, verbose_name=_("Станция"), on_delete=models.PROTECT)
    token = models.ForeignKey(Token, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(_("Время"))

    class Meta:
        verbose_name = _("Запрос на авторизация")
        verbose_name_plural = _("Запросы на авторизация")


class PriceChargePointConnector(TimeStampedModel):
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


class CommentsChargePoint(TimeStampedModel):
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


class FavoriteChargePoint(TimeStampedModel):
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


class FavoriteAddress(TimeStampedModel):
    address = models.ForeignKey(
        Location, verbose_name=_("Адрес"), related_name="user_favorites", on_delete=models.PROTECT
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


class ChargePointTask(TimeStampedModel):
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
