from django.contrib import admin

from apps.locations.models import Location, ChargePoint, Connector


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(ChargePoint)
class ChargePointAdmin(admin.ModelAdmin):
    list_display = ("name", "identity")

@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    list_display = ("charge_point", "connector_id", "standard", "format")
