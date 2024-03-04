from django.db import models
from django.utils.translation import gettext as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


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
    region = models.ForeignKey(to=Region, verbose_name=_("Region"), on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']
        verbose_name = _("District")
        verbose_name_plural = _("District")

