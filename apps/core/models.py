from django.db import models
from django.utils.translation import gettext as _


class QrCodeScanerCount(models.Model):
    count = models.IntegerField(_("Сканлаган QR кодлар сони"), null=True, blank=True)
    iphone = models.IntegerField(_("Iphone"), default=0)
    android = models.IntegerField(_("Android"), default=0)
    last_scan = models.DateTimeField(_("Сканлаган сана"), auto_now=True)

    class Meta:
        verbose_name = _("QR кодлар сони")
        verbose_name_plural = _("QR кодлар сони")

    def __str__(self):
        return str(self.count)


class Media(models.Model):
    image = models.ImageField(_("Фото"), upload_to="%Y/%m/%d")

    class Meta:
        verbose_name = _("Фото")
        verbose_name_plural = _("Фото")

    def __str__(self):
        return self.image.name
