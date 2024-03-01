from django.db import models
from django.utils.translation import gettext as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


class QrCodeScanerCount(TimeStampedModel):
    count = models.IntegerField(_("Сканлаган QR кодлар сони"), null=True, blank=True)
    iphone = models.IntegerField(_("Iphone"), default=0)
    android = models.IntegerField(_("Android"), default=0)
    last_scan = models.DateTimeField(_("Сканлаган сана"), auto_now=True)

    class Meta:
        verbose_name = _("QR кодлар сони")
        verbose_name_plural = _("QR кодлар сони")

    def __str__(self):
        return str(self.count)


class Media(TimeStampedModel):
    image = models.ImageField(_("Фото"), upload_to="%Y/%m/%d")

    class Meta:
        verbose_name = _("Фото")
        verbose_name_plural = _("Фото")

    def __str__(self):
        return self.image.name


class MinBalance(TimeStampedModel):
    amount = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Min Balance")
        verbose_name_plural = _("Min Balances")
