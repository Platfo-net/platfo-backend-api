class TelegramBotCommand:
    START = {
        "command": "/start",
        "description": "Start",
    }

    SEND_DIRECT_MESSAGE = {
        "command": "/send_direct_message_helper",
        "description": "Send direct message to shop support"
    }

    commands = [START, SEND_DIRECT_MESSAGE]
