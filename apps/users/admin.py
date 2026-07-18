from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BusinessProfile, CourierProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Giftly", {"fields": ("role", "phone")}),
    )


admin.site.register(BusinessProfile)
admin.site.register(CourierProfile)
