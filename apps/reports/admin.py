from django.contrib import admin
from .models import Category, Report


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'icon']
    search_fields = ['name_ar', 'name_en']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'status', 'category', 'country', 'city', 'reporter', 'created_at']
    list_filter = ['type', 'status', 'category', 'country']
    search_fields = ['title', 'description', 'reporter__username']
    autocomplete_fields = ['reporter']
    date_hierarchy = 'created_at'
