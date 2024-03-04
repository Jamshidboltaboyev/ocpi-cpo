from apps.core.models import TimeStampedModel, Image
from django.db import models
from django.utils.translation import gettext as _


class Credentials(TimeStampedModel):
    token = models.CharField(max_length=64)
    url = models.URLField(max_length=255)

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = _("Credentials")
        verbose_name_plural = _("Credentials")
        ordering = ['-updated_at']


class BusinessDetails(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    website = models.URLField(max_length=255, verbose_name=_("Website"))
    logo = models.ForeignKey(to=Image, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Logo"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Business Detail")
        verbose_name_plural = _("Business Details")
        ordering = ('name',)


class CredentialsRole(TimeStampedModel):
    class Roles(models.TextChoices):
        CPO = 'CPO'  # Charge Point Operator Role
        EMSP = 'EMSP'  # eMobility Service Provider Role
        HUB = 'HUB'  # Hub role
        NAP = 'NAP'  # National Access Point Role (national Database with all Location information of a country)
        NSP = 'NSP'  # Navigation Service Provider Role, role like an eMSP (probably only interested in Location
        # information
        OTHER = 'OTHER'  # Other role
        SCSP = 'SCSP'  # Smart Charging Service Provider Role

    credentials = models.ForeignKey(to=Credentials, on_delete=models.PROTECT)
    role = models.CharField(max_length=10, choices=Roles.choices, verbose_name=_("Role"))
    business_details = models.ForeignKey(to=BusinessDetails, on_delete=models.PROTECT)
    party_id = models.CharField(max_length=3, verbose_name=_("Party id"))
    country_code = models.CharField(max_length=2, verbose_name=_("Country code"))

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Credentials Role")
        verbose_name_plural = _("Credentials Roles")
        ordering = ('-updated_at',)
