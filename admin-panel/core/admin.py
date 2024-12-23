from django.contrib import admin

from . import models


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
        "user", "title", "description", "category", "is_info_required"
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


class ShopTelegramBotAdmin(admin.ModelAdmin):
    model = models.ShopShopTelegramBots
    list_display = (
        "shop", "telegram_bot"
    )


class TelegramBotAdmin(admin.ModelAdmin):
    model = models.TelegramBots
    list_display = (
        "user", "username"
    )


class OrderItemInline(admin.TabularInline):
    model = models.ShopOrderItems
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    model = models.ShopOrders
    inlines = [OrderItemInline]
    exclude = ["order_number"]
    list_display = (
        "shop", "order_number", "status"
    )


class SocialTelegramLeadAdmin(admin.ModelAdmin):
    model = models.SocialTelegramLeads
    list_display = (
        "username", "telegram_bot"
    )


class SocialTelegramLeadMessagesAdmin(admin.ModelAdmin):
    model = models.SocialTelegramLeadMessages
    list_display = (
        "message", "lead"
    )


class ShopPaymentMethodAdmin(admin.ModelAdmin):
    model = models.ShopPaymentMethods
    list_display = (
        "title",
    )


class ShopShopPaymentMethodAdmin(admin.ModelAdmin):
    model = models.ShopShopPaymentMethods
    list_display = (
        "shop", "payment_method", "is_active"
    )


class CreditPlansAdmin(admin.ModelAdmin):
    model = models.CreditPlans
    list_display = (
        "title", "discounted_price", "currency",
    )


class ShopShipmentMethodsAdmin(admin.ModelAdmin):
    model = models.ShopShipmentMethods
    list_display = (
        "title", "price", "is_active", "shop"
    )


admin.site.register(models.Users, UserAdmin)
admin.site.register(models.ShopShops, ShopAdmin)
admin.site.register(models.CreditShopCredits, CreditShopAdmin)
admin.site.register(models.ShopCategories, ShopCategoryAdmin)
admin.site.register(models.ShopProducts, ShopProductAdmin)
admin.site.register(models.ShopShopTelegramBots, ShopTelegramBotAdmin)
admin.site.register(models.TelegramBots, TelegramBotAdmin)
admin.site.register(models.ShopOrders, OrderAdmin)
admin.site.register(models.SocialTelegramLeads, SocialTelegramLeadAdmin)
admin.site.register(models.SocialTelegramLeadMessages, SocialTelegramLeadMessagesAdmin)
admin.site.register(models.ShopPaymentMethods, ShopPaymentMethodAdmin)
admin.site.register(models.ShopShopPaymentMethods, ShopShopPaymentMethodAdmin)
admin.site.register(models.CreditPlans, CreditPlansAdmin)
admin.site.register(models.ShopShipmentMethods, ShopShipmentMethodsAdmin)
