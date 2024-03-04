from django.contrib import admin

from apps.credentials.models import Credentials, BusinessDetails, CredentialsRole


@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ['token', 'url']


@admin.register(BusinessDetails)
class BusinessDetailsAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']


@admin.register(CredentialsRole)
class CredentialsRoleAdmin(admin.ModelAdmin):
    list_display = ['credentials', 'role']

