from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class MisfoundUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات إضافية', {'fields': ('phone', 'country', 'city')}),
    )
    list_display = ['username', 'email', 'phone', 'country', 'city', 'is_staff']
