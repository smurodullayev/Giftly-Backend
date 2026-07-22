from django.contrib import admin
from .models import Region, District, Address

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'created_at', 'updated_at')
    search_fields = ('name', 'region__name')
    ordering = ('region__name', 'name')
    list_filter = ('region',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('region', 'district', 'address_line', 'latitude', 'longitude', 'created_at', 'updated_at')
    search_fields = ('region__name', 'district__name', 'address_line')
    ordering = ('region__name', 'district__name', 'address_line')
    list_filter = ('region', 'district')