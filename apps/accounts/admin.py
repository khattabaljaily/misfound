from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class MisfoundUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (_('معلومات إضافية'), {'fields': ('phone', 'country', 'city')}),
    )
    list_display = ['username', 'email', 'phone', 'country', 'city', 'is_staff']
