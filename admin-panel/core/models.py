from uuid import uuid4
from django.db import models


class AcademyCategories(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    parent = models.ForeignKey(
        'self', models.DO_NOTHING, blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'academy_categories'


class AcademyContentCategories(models.Model):
    id = models.UUIDField(primary_key=True)
    content = models.ForeignKey(
        'AcademyContents', models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(
        AcademyCategories, models.DO_NOTHING, blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'academy_content_categories'


class AcademyContentLabels(models.Model):
    id = models.UUIDField(primary_key=True)
    content = models.ForeignKey(
        'AcademyContents', models.DO_NOTHING, blank=True, null=True)
    label = models.ForeignKey(
        'AcademyLabels', models.DO_NOTHING, blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'academy_content_labels'


class AcademyContents(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=1024, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    # This field type is a guess.
    blocks = models.TextField(blank=True, null=True)
    slug = models.CharField(max_length=300, blank=True, null=True)
    is_published = models.BooleanField(blank=True, null=True)
    cover_image = models.CharField(max_length=1024, blank=True, null=True)
    time = models.CharField(max_length=200, blank=True, null=True)
    version = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'academy_contents'


class AcademyLabels(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'academy_labels'


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'


class BotBuilderChatflows(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_builder_chatflows'


class BotBuilderEdges(models.Model):
    from_id = models.UUIDField(blank=True, null=True)
    to_id = models.UUIDField(blank=True, null=True)
    from_port = models.UUIDField(blank=True, null=True)
    to_port = models.UUIDField(blank=True, null=True)
    from_widget = models.UUIDField(blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    chatflow = models.ForeignKey(
        BotBuilderChatflows, models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_builder_edges'


class BotBuilderNodes(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    chatflow = models.ForeignKey(
        BotBuilderChatflows, models.DO_NOTHING, blank=True, null=True)
    # This field type is a guess.
    from_widget = models.TextField(blank=True, null=True)
    # This field type is a guess.
    widget = models.TextField(blank=True, null=True)
    # This field type is a guess.
    quick_replies = models.TextField(blank=True, null=True)
    is_head = models.BooleanField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_builder_nodes'


class BotBuilderNodeuies(models.Model):
    text = models.CharField(max_length=255, blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    # This field type is a guess.
    data = models.TextField(blank=True, null=True)
    # This field type is a guess.
    ports = models.TextField(blank=True, null=True)
    has_delete_action = models.BooleanField(blank=True, null=True)
    has_edit_action = models.BooleanField(blank=True, null=True)
    chatflow = models.ForeignKey(
        BotBuilderChatflows, models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bot_builder_nodeuies'


class Connections(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    application_name = models.CharField(max_length=255, blank=True, null=True)
    account_id = models.BigIntegerField(blank=True, null=True)
    # This field type is a guess.
    details = models.TextField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'connections'


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


class CreditPlans(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    extend_days = models.IntegerField(blank=True, null=True)
    extend_count = models.IntegerField(blank=True, null=True)
    original_price = models.FloatField()
    discounted_price = models.FloatField()
    discount_percentage = models.FloatField()
    is_discounted = models.FloatField()
    currency = models.CharField(max_length=10)
    module = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'credit_plans'


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


class DataboardCommentStats(models.Model):
    facebook_page_id = models.BigIntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    from_datetime = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'databoard_comment_stats'


class DataboardFollowerStats(models.Model):
    facebook_page_id = models.BigIntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    from_datetime = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'databoard_follower_stats'


class DataboardLeadMessageStats(models.Model):
    facebook_page_id = models.BigIntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    from_datetime = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'databoard_lead_message_stats'


class DataboardLeadStats(models.Model):
    facebook_page_id = models.BigIntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    from_datetime = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'databoard_lead_stats'


class DataboardLiveCommentStats(models.Model):
    facebook_page_id = models.BigIntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    from_datetime = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'databoard_live_comment_stats'


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


class LiveChatLeads(models.Model):
    lead_igs_id = models.BigIntegerField(blank=True, null=True)
    facebook_page_id = models.BigIntegerField(blank=True, null=True)
    last_message = models.CharField(max_length=1024, blank=True, null=True)
    last_message_at = models.DateTimeField(blank=True, null=True)
    last_interaction_at = models.DateTimeField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    profile_image = models.CharField(max_length=1024, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    is_verified_user = models.BooleanField(blank=True, null=True)
    is_user_follow_business = models.BooleanField(blank=True, null=True)
    is_business_follow_user = models.BooleanField(blank=True, null=True)
    first_impression = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'live_chat_leads'


class LiveChatMessages(models.Model):
    from_page_id = models.BigIntegerField(blank=True, null=True)
    to_page_id = models.BigIntegerField(blank=True, null=True)
    type = models.CharField(max_length=32, blank=True, null=True)
    # This field type is a guess.
    content = models.TextField(blank=True, null=True)
    mid = models.CharField(max_length=256, blank=True, null=True)
    send_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'live_chat_messages'


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


class NotifierCampaignLeads(models.Model):
    lead_igs_id = models.BigIntegerField(blank=True, null=True)
    is_sent = models.BooleanField(blank=True, null=True)
    is_seen = models.BooleanField(blank=True, null=True)
    mid = models.CharField(max_length=255, blank=True, null=True)
    reaction = models.CharField(max_length=100, blank=True, null=True)
    lead = models.ForeignKey(
        LiveChatLeads, models.DO_NOTHING, blank=True, null=True)
    campaign = models.ForeignKey(
        'NotifierCampaigns', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notifier_campaign_leads'


class NotifierCampaigns(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    is_draft = models.BooleanField(blank=True, null=True)
    facebook_page_id = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    # This field type is a guess.
    content = models.TextField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    # This field type is a guess.
    leads_criteria = models.TextField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notifier_campaigns'


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
    payment_reference_number = models.CharField(
        max_length=255, blank=True, null=True)
    payment_card_last_four_number = models.CharField(
        max_length=16, blank=True, null=True)
    payment_datetime = models.DateTimeField(blank=True, null=True)
    payment_receipt_image = models.CharField(
        max_length=255, blank=True, null=True)
    shipment_method = models.ForeignKey(
        'ShopShipmentMethods', models.DO_NOTHING, blank=True, null=True)
    payment_method = models.ForeignKey(
        'ShopPaymentMethods', models.DO_NOTHING, blank=True, null=True)

    def save(self, *args, **kwargs):
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
    shop = models.ForeignKey(
        'ShopShops', models.DO_NOTHING, blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shop_payment_methods'


class ShopProducts(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    currency = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
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
    price = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=255, blank=True, null=True)
    shop = models.ForeignKey(
        'ShopShops', models.DO_NOTHING, blank=True, null=True)
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
        return self.telegram_bot

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
    Users, TelegramBots, SocialTelegramLeads,
    ShopShops, ShopShopTelegramBots,
    ShopShipmentMethods, ShopProducts, ShopPaymentMethods, ShopOrders, ShopOrderItems,
    CreditShopCredits, ShopCategories, Roles,
]
