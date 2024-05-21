from uuid import uuid4

from django.db import models


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'


class CreditInvoices(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    payed_at = models.DateTimeField(blank=True, null=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=10)
    bought_on_discount = models.BooleanField(blank=True, null=True)
    plan_name = models.CharField(max_length=255, blank=True, null=True)
    module = models.CharField(max_length=255, blank=True, null=True)
    extend_days = models.IntegerField(blank=True, null=True)
    extend_count = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'credit_invoices'


class CreditPlanFeatures(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    plan = models.ForeignKey('CreditPlans', models.DO_NOTHING)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'credit_plan_features'


CREDIT_PLAN_MODULE_CHOICES = (
    ("NOTIFIER", 'NOTIFIER'),
    ("TELEGRAM_SHOP", 'TELEGRAM_SHOP')
)

CURRENCY_CHOICES = (
    ("IRR", "ریال"),
)


class CreditPlans(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    extend_days = models.IntegerField(blank=True, null=True)
    extend_count = models.IntegerField(blank=True, null=True)
    original_price = models.FloatField()
    discounted_price = models.FloatField()
    discount_percentage = models.FloatField()
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    module = models.CharField(max_length=255, choices=CREDIT_PLAN_MODULE_CHOICES)
    created_at = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True, default=uuid4)

    class Meta:
        managed = False
        db_table = 'credit_plans'

        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'


class CreditShopCredits(models.Model):
    shop = models.OneToOneField('ShopShops', models.DO_NOTHING)
    expires_at = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return self.shop.title

    class Meta:
        managed = False
        db_table = 'credit_shop_credits'
        verbose_name = 'Shop Credit'
        verbose_name_plural = 'Shop Credits'


class InstagramPages(models.Model):
    facebook_user_long_lived_token = models.CharField(
        max_length=255, blank=True, null=True)
    facebook_user_id = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    facebook_page_id = models.BigIntegerField(blank=True, null=True)
    instagram_page_id = models.BigIntegerField(blank=True, null=True)
    facebook_page_token = models.CharField(
        max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    profile_picture_url = models.CharField(
        max_length=1024, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    website = models.CharField(max_length=128, blank=True, null=True)
    ig_id = models.CharField(max_length=128, blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    follows_count = models.IntegerField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    leads_count = models.IntegerField(blank=True, null=True)
    comments_count = models.IntegerField(blank=True, null=True)
    live_comment_count = models.IntegerField(blank=True, null=True)
    chats_count = models.IntegerField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'instagram_pages'


class NotificationUsers(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    notification = models.ForeignKey(
        'Notifications', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notification_users'


class Notifications(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_visible = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notifications'


class Roles(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    persian_name = models.CharField(max_length=100, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'roles'


class ShopCategories(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(max_length=255, blank=True, null=True)
    shop = models.ForeignKey(
        'ShopShops', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        managed = False
        db_table = 'shop_categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class ShopOrderItems(models.Model):
    order = models.ForeignKey(
        'ShopOrders', models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(
        'ShopProducts', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    product_title = models.CharField(max_length=256, blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True, default=uuid4)
    count = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    currency = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shop_order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'


status_choices = (
    ("UNPAID", "UNPAID"),
    ("ACCEPTED", "ACCEPTED"),
    ("PAYMENT_CHECK", "PAYMENT_CHECK"),
    ("PREPARATION", "PREPARATION"),
    ("SENT", "SENT"),
    ("DECLINED", "DECLINED"),
)


class ShopOrders(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True, choices=status_choices)
    order_number = models.IntegerField(blank=True, null=True)
    lead = models.ForeignKey('SocialTelegramLeads',
                             models.DO_NOTHING, blank=True, null=True)
    shop = models.ForeignKey(
        'ShopShops', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True, default=uuid4)
    shipment_method = models.ForeignKey(
        'ShopShipmentMethods', models.DO_NOTHING, blank=True, null=True)
    shop_payment_method = models.ForeignKey(
        'ShopShopPaymentMethods', models.DO_NOTHING, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True)
    payment_information = models.TextField(null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            last_order = ShopOrders.objects.filter(shop=self.shop).order_by("order_number").last()
            order_number = 10000000
            if last_order:
                order_number = last_order.order_number + 1
            self.order_number = order_number
        super().save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'shop_orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class ShopPaymentMethods(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)
    information_fields = models.TextField(blank=True, null=True)  # This field type is a guess.
    payment_fields = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'shop_payment_methods'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'

    def __str__(self) -> str:
        return f"{self.title}"


class ShopShopPaymentMethods(models.Model):
    shop = models.ForeignKey('ShopShops', models.DO_NOTHING, blank=True, null=True)
    payment_method = models.ForeignKey(
        ShopPaymentMethods, models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.shop} : {self.payment_method}"

    class Meta:
        managed = False
        db_table = 'shop_shop_payment_methods'
        verbose_name = 'Shop Payment Method'
        verbose_name_plural = 'Shop Payment Methods'


class ShopProducts(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    currency = models.CharField(max_length=32, blank=True, null=True, default="IRR")
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True, default=True)
    is_available = models.BooleanField(blank=True, null=True, default=True)
    category = models.ForeignKey(
        ShopCategories, models.DO_NOTHING, blank=True, null=True)
    shop = models.ForeignKey(
        'ShopShops', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        managed = False
        db_table = 'shop_products'


class ShopShipmentMethods(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    currency = models.CharField(max_length=255, blank=True, null=True)
    shop = models.ForeignKey(
        'ShopShops', models.DO_NOTHING, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shop_shipment_methods'


class ShopShopTelegramBots(models.Model):
    support_token = models.CharField(max_length=255, blank=True, null=True)
    support_bot_token = models.CharField(max_length=255, blank=True, null=True)
    support_account_chat_id = models.BigIntegerField(blank=True, null=True)
    is_support_verified = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    shop = models.ForeignKey(
        'ShopShops', models.DO_NOTHING, blank=True, null=True)
    telegram_bot = models.ForeignKey(
        'TelegramBots', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return "bot"

    class Meta:
        managed = False
        db_table = 'shop_shop_telegram_bots'
        verbose_name = 'Shop Telegram Bot'
        verbose_name_plural = 'Shop Telegram Bots'


class ShopShops(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)
    is_info_required = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    class Meta:
        managed = False
        db_table = 'shop_shops'
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'


class SocialTelegramLeads(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    chat_id = models.BigIntegerField(blank=True, null=True)
    lead_number = models.BigIntegerField(blank=True, null=True)
    telegram_bot = models.ForeignKey(
        'TelegramBots', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return self.username

    class Meta:
        managed = False
        db_table = 'social_telegram_leads'
        verbose_name = 'Social Telegram Lead'
        verbose_name_plural = 'Social Telegram Leads'


class SocialTelegramLeadMessages(models.Model):
    lead = models.ForeignKey('SocialTelegramLeads', models.DO_NOTHING, blank=True, null=True)
    is_lead_to_bot = models.BooleanField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    message_id = models.BigIntegerField(blank=True, null=True)
    mirror_message_id = models.BigIntegerField(blank=True, null=True)
    reply_to_id = models.BigIntegerField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return self.message

    class Meta:
        managed = False
        db_table = 'social_telegram_lead_messages'
        verbose_name = 'Social Telegram Lead Message'
        verbose_name_plural = 'Social Telegram Lead Messages'


class TelegramBots(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    bot_token = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    bot_id = models.BigIntegerField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return self.username

    class Meta:
        managed = False
        db_table = 'telegram_bots'
        verbose_name = 'Telegram Bot'
        verbose_name_plural = 'Telegram Bots'


class Users(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(
        unique=True, max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    phone_country_code = models.CharField(max_length=5, blank=True, null=True)
    hashed_password = models.CharField(max_length=255)
    is_active = models.BooleanField(blank=True, null=True)
    is_email_verified = models.BooleanField(blank=True, null=True)
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(Roles, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self) -> str:
        return f"+{self.phone_country_code}-{self.phone_number}"

    class Meta:
        managed = False
        db_table = 'users'
        unique_together = (('phone_country_code', 'phone_number'),)
        verbose_name = 'User'
        verbose_name_plural = 'Users'


models_list = [
    Users, TelegramBots, SocialTelegramLeads, SocialTelegramLeadMessages,
    ShopShops, ShopShopTelegramBots,
    ShopShipmentMethods, ShopProducts, ShopPaymentMethods,
    ShopShopPaymentMethods, ShopOrders, ShopOrderItems,
    CreditShopCredits, ShopCategories, Roles, CreditPlans
]
