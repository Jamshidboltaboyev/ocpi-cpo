from django.core.validators import MinLengthValidator
from django.db import models
from apps.core.models import TimeStampedModel
from apps.cdrs.models import CdrToken
from apps.locations.models import Location, ChargePoint


class Session(TimeStampedModel):
    class AuthMethod(models.TextChoices):
        AUTH_REQUEST = "AUTH_REQUEST"
        COMMAND = "COMMAND"
        WHITELIST = "WHITELIST"

    country_code = models.CharField(max_length=2, validators=[MinLengthValidator(2)])
    party_id = models.CharField(max_length=3, validators=[MinLengthValidator(3)])
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField(null=True, blank=True)
    kwh = models.FloatField()
    cdr_token = models.ForeignKey(to=CdrToken, on_delete=models.PROTECT)
    auth_method = models.CharField(max_length=30, choices=AuthMethod.choices)
    authorization_reference = models.CharField(max_length=36, null=True, blank=True)
    location = models.ForeignKey(to=Location, on_delete=models.PROTECT)
    evse = models.ForeignKey(to=ChargePoint, on_delete=models.PROTECT)
    connector_id = models.CharField(max_length=36)
    meter_id = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=3)
    charging_periods = models.JSONField(default=list)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=30)

    class Meta:
        ordering = ['-start_date_time']
        verbose_name = 'Sessions'
        verbose_name_plural = 'Sessions'

    def __str__(self):
        return self.id
