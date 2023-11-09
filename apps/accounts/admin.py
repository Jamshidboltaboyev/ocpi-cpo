from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Otp, UserLoginDevice, QrCodeScanerCount, UserGift, DeletedAccount


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': (
            'phone', 'full_name', 'birth_date', 'first_name', 'last_name', 'father_name', 'avatar', 'user_type',
            'password', 'last_login', 'free_charging_time', 'free_charging_to_date', 'amount')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('phone', 'password1', 'password2')
            }
        ),
    )

    list_display = ('phone', 'is_staff', 'last_login', 'amount')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('phone',)
    ordering = ('phone',)
    readonly_fields = ('free_charging_time',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(User, UserAdmin)
admin.site.register(UserLoginDevice)


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message_id', 'code', 'sent_time')


@admin.register(QrCodeScanerCount)
class QrCodeScanerCountAdmin(admin.ModelAdmin):
    list_display = ('count', 'iphone', 'android', 'last_scan')


@admin.register(UserGift)
class UserGiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'expired_date')


@admin.register(DeletedAccount)
class DeletedAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'reason')
