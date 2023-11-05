class TelegramBotCommand:
    START = {
        "command": "/start",
        "description": "شروع",
    }

    SEND_DIRECT_MESSAGE = {
        "command": "/send_direct_message_helper",
        "description": "ارسال پیام مستقیم به پشتیبانی"
    }

    VITRIN = {
        "command": "/vitrin",
        "description": "ویترین"
    }

    commands = [START, SEND_DIRECT_MESSAGE, VITRIN]
