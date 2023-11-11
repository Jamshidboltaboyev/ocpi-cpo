from django.contrib import admin
from .models import VehicleModel


@admin.register(VehicleModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "manufacturer", "user_defined", 'vehicle_count']
    search_fields = ["name"]
    list_filter = ['manufacturer']

    def vehicle_count(self, obj):
        return obj
