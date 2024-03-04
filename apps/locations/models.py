from django.db import models
from django.utils.translation import gettext as _

from apps.core.models import TimeStampedModel, District


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
    name = models.CharField(max_length=40, null=True, verbose_name=_("Name"))

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
        verbose_name = _("Connector")
        verbose_name_plural = _("Connector")
        ordering = ["id"]

    def __str__(self):
        return f"{self.charge_point}: № {self.connector_id}"
