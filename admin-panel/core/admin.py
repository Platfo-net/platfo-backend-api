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


class CreditShopAdmin(admin.ModelAdmin):
    model = models.CreditShopCredits
    list_display = (
        "shop", "expires_at"
    )
    search_fields = ("shop",)


class ShopCategoryAdmin(admin.ModelAdmin):
    model = models.ShopCategories
    list_display = (
        "shop", "title",
    )
    search_fields = ("shop", "title")


class ShopProductAdmin(admin.ModelAdmin):
    model = models.ShopProducts
    list_display = (
        "shop", "title", "category", "get_price"
    )

    def get_price(self, obj: models.ShopProducts):
        return f"{obj.price} {obj.currency}"
    search_fields = ("shop", "title")


admin.site.register(models.Users, UserAdmin)
admin.site.register(models.ShopShops, ShopAdmin)
admin.site.register(models.CreditShopCredits, CreditShopAdmin)
admin.site.register(models.ShopCategories, ShopCategoryAdmin)
