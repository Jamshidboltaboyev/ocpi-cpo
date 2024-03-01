from django.db import models
from apps.core.models import TimeStampedModel
from django.utils.translation import gettext as _


class PriceComponent(TimeStampedModel):
    type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    step_size = models.IntegerField()


class TariffRestrictions(TimeStampedModel):
    start_time = models.CharField(max_length=5, null=True, blank=True)
    end_time = models.CharField(max_length=5, null=True, blank=True)
    start_date = models.CharField(max_length=10, null=True, blank=True)
    end_date = models.CharField(max_length=10, null=True, blank=True)
    min_kwh = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_kwh = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_current = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_current = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_power = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_power = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_duration = models.IntegerField(null=True, blank=True)
    max_duration = models.IntegerField(null=True, blank=True)
    day_of_week = models.JSONField(default=list)
    reservation = models.CharField(max_length=50, null=True, blank=True)


class TariffElement(TimeStampedModel):
    restrictions = models.OneToOneField(TariffRestrictions, null=True, blank=True, on_delete=models.CASCADE)
    price_components = models.ManyToManyField(PriceComponent)


def tariff_alt_text_default():
    return {"language": "en", "text": "Standard Tariff"}


def price_default():
    return {'excl_vat': 0, ' incl_vat': 0}


class Tariff(TimeStampedModel):
    class TariffType(models.TextChoices):
        AD_HOC_PAYMENT = 'AD_HOC_PAYMENT'  # Ad-hoc Payment
        PROFILE_CHEAP = 'PROFILE_CHEAP'  # Profile Cheap
        PROFILE_FAST = 'PROFILE_FAST'  # Profile Fast
        PROFILE_GREEN = 'PROFILE_GREEN'  # Profile Green
        REGULAR = 'REGULAR'  # Regular

    currency = models.CharField(max_length=3, verbose_name=_("ISO-4217 code of the currency of this tariff."))
    type = models.CharField(max_length=50, choices=TariffType.choices, null=True, blank=True)
    tariff_alt_url = models.URLField(null=True, blank=True)
    tariff_alt_text = models.JSONField(default=tariff_alt_text_default)

    min_price = models.JSONField(default=price_default)
    max_price = models.JSONField(default=price_default)

    elements = models.ManyToManyField(TariffElement)
    start_date_time = models.DateTimeField(null=True, blank=True)
    end_date_time = models.DateTimeField(null=True, blank=True)
    energy_mix = models.JSONField(null=True, blank=True)
    last_updated = models.DateTimeField()
