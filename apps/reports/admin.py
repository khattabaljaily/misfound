from django.contrib import admin
from .models import Category, Match, Report


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name_en', 'icon']
    search_fields = ['name_ar', 'name_en']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'status', 'category', 'country', 'city', 'reporter', 'created_at']
    list_filter = ['type', 'status', 'category', 'country']
    search_fields = ['title', 'description', 'identifier', 'reporter__username']
    autocomplete_fields = ['reporter']
    date_hierarchy = 'created_at'


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['lost_report', 'found_report', 'score', 'created_at']
    list_filter = ['score']
    search_fields = ['lost_report__title', 'found_report__title', 'reason']
    autocomplete_fields = ['lost_report', 'found_report']
