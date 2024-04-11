

class MessageStatus:
    BUILDING = "BUILDING"
    FINISHED = "FINISHED"
    REMOVED = "REMOVED"


class MessageBuilderCommand:
    CANCEL_MESSAGE = {
        "command": "/cancel_message",
        "description": "لغو پیام",
    }

    NEW_MESSAGE = {
        "command": "/new_message",
        "description": "پیام جدید",
    }

    START = {
        "command": "/start",
        "description": "start",
    }


class MessageBuilderButton:
    CANCEL_MESSAGE = {
        "title": "حذف پیام",
        "command": "CANCEL_MESSAGE"
    }
    FINISH_MESSAGE = {
        "title": "اتمام پیام",
        "command": "FINISH_MESSAGE"
    }


class MessageBuilderTelegramMessage:
    ERROR_NOT_FINISHED_MESSAGE_EXIST = "شما پیامی در حال ساخت دارید. برای ساخت پیام جدید ابتدا پیام قبلی را تمام و یا لغو کنید."  # noqa
    ERROR_NOT_BUILDING_MESSAGE_EXIST = "شما پیام در حال ساختی ندارید."
    CANCEL_MESSAGE_SUCCESSFULLY = "ساخت پیام شما با موفقیت لغو شد. "
    CANCEL_MESSAGE_CHECK = "آیا مطمئن هستید؟"

    ERROR_MESSAGE_NOT_FOUND = "پیام مدنظر یافت نشد و یا پاک شده است."

    ENTER_MESSAGE_TEXT = "لطفا متن پیام خود را وارد کنید."
    ENTER_URL = "لطفا آدرس url مورد نظر را وارد کنید."
    ENTER_IMAGE = "در صورت تمایل عکس مورد نظر را آپلود کنید. در غیر این صورت روی دکمه ی اتمام پیام کلیک کنید."  # noqa

    MESSAGE_CREATED_SUCCESSFULLY = "پیام شما با موفقیت ساخته شد."
