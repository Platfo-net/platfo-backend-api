class TelegramSupportBotCommand:
    START = {
        "command": "/start",
        "description": "Start",
    }
    PAYMANE_CHECK_ORDERS = {
        "command": "/payment_check_orders",
        "description": "Payment Check Orders",
    }

    UNPAID_ORDERS = {
        "command": "/unpaid_orders",
        "description": "Unpaid Orders",
    }

    ACCEPTED_ORDERS = {
        "command": "/accepted_orders",
        "description": "Accepted Orders",
    }

    commands = [
        START, PAYMANE_CHECK_ORDERS, UNPAID_ORDERS, ACCEPTED_ORDERS
    ]
