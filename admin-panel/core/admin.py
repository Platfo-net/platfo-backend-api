from django.contrib import admin
from core import models


class UserAdmin(admin.ModelAdmin):
    model = models.Users
    list_display = (
        "first_name", "last_name",
        "phone_country_code", "phone_number",
        "is_active", "is_email_verified", "role"
    )


class ShopAdmin(admin.ModelAdmin):
    model = models.ShopShops
    list_display = (
        "user", "title", "description", "category"
    )


admin.site.register(models.Users, UserAdmin)
admin.site.register(models.ShopShops, ShopAdmin)
