

class TelegramCallbackCommand:
    ACCEPT_ORDER = {

        "title": {
            "fa": "تایید سفارش",
        },
        "command": "ACCEPT_ORDER"
    }
    DECLINE_ORDER = {
        "title": {
            "fa": "رد سفارش",
        },
        "command": "DECLINE_ORDER"
    }
    DECLINE_PAYMENT_ORDER = {
        "title": {
            "fa": "رد پرداخت سفارش",
        },
        "command": "DECLINE_PAYMENT_ORDER"
    }
    ACCEPT_SHOP_SUPPORT_ACCOUNT = {
        "title":
            {
                "fa": "OK",
            },

        "command": "ACCEPT_SHOP"
    }
    PREPARE_ORDER = {
        "title":
            {
                "fa": "آماده سازی سفارش",
            },

        "command": "PREPARE_ORDER"
    }
    SEND_ORDER = {
        "title":
            {
                "fa": "ارسال سفارش",
            },

        "command": "SEND_ORDER"
    }
    
    SEND_DIRECT_MESSAGE = {
        "title":
            {
                "fa": "ارسال پیام به مشتری",
            },

        "command": "SEND_DIRECT_MESSAGE"
    }
