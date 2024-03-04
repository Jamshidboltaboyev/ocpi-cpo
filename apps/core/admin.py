from django.contrib import admin

from apps.core.models import Country, Region, District, Image


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['url']
