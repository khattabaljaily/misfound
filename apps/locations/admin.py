from django.contrib import admin
from .models import Country, City


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'code']
    search_fields = ['name_ar', 'name_en', 'code']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'country']
    list_filter = ['country']
    search_fields = ['name_ar', 'name_en']
