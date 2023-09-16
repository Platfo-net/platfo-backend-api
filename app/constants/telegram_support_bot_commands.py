class TelegramSupportBotCommand:
    START = {
        "command": "/start",
        "description": "Start",
    }
    PAID_ORDERS = {
        "command": "/paid_orders",
        "description": "Paid Orders",
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
        START, PAID_ORDERS, UNPAID_ORDERS, ACCEPTED_ORDERS
    ]
