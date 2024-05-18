class TelegramBotCommand:
    START = {"command": "/start", "description": "شروع", }

    SEND_DIRECT_MESSAGE = {
        "command": "/send_direct_message_helper",
        "description": "ارسال پیام مستقیم به پشتیبانی"
    }

    CONNECT_TO_ASSISTANT = {
        "command": "/connect_to_assistant",
        "description": "اتصال به دستیار هوشمند"
    }

    VITRIN = {"command": "/vitrin", "description": "ویترین"}

    commands = [START, VITRIN, SEND_DIRECT_MESSAGE, CONNECT_TO_ASSISTANT]
    commands_text = [command["command"] for command in commands]
