from django.contrib import admin
from .models import QrCodeScanerCount


@admin.register(QrCodeScanerCount)
class QrCodeScanerCountAdmin(admin.ModelAdmin):
    list_display = ('count', 'iphone', 'android', 'last_scan')
