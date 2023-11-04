class TelegramSupportBotCommand:
    START = {
        "command": "/start",
        "description": "شروع",
    }
    CREDIT_EXTENDING = {
        "command": "/extend_credit",
        "description": "افزایش اعتبار",
    }
    PAYMENT_CHECK_ORDERS = {
        "command": "/payment_check_orders",
        "description": " سفارشات در انتظار تعیین وضعیت پرداخت",
    }

    UNPAID_ORDERS = {
        "command": "/unpaid_orders",
        "description": "سفارشات پرداخت نشده",
    }

    ACCEPTED_ORDERS = {
        "command": "/accepted_orders",
        "description": "سفارشات تایید شده",
    }

    SEARCH_ORDER = {
        "command": "/search_order",
        "description": "جستجوی سفارشات",
    }
    HELP_DIRECT_MESSAGE = {
        "command": "/help_send_direct_message",
        "description": "ارسال پیام مستقیم",
    }

    commands = [
        START, CREDIT_EXTENDING, PAYMENT_CHECK_ORDERS, UNPAID_ORDERS, ACCEPTED_ORDERS,
        SEARCH_ORDER, HELP_DIRECT_MESSAGE
    ]
