class OrderStatus:
    UNPAID = {
        "value": "UNPAID",
        "title": {
            "fa": "پرداخت نشده",
            "en": "unpaid"
        }
    }
    PAYMENT_CHECK = {
        "value": "PAYMENT_CHECK",
        "title": {
            "fa": "بررسی پرداخت",
            "en": "payment check"
        }
    }
    ACCEPTED = {
        "value": "ACCEPTED",
        "title": {
            "fa": "قبول شده",
            "en": "accepted"
        }
    }
    PREPARATION = {
        "value": "PREPARATION",
        "title": {
            "fa": "در حال آماده سازی",
            "en": "preparation"
        }
    }
    SENT = {
        "value": "SENT",
        "title": {
            "fa": "ارسال شده",
            "en": "sent"
        }
    }
    DECLINED = {
        "value": "DECLINED",
        "title": {
            "fa": "رد شده",
            "en": "declined"
        }
    }

    PAYMENT_DECLINED = {
        "value": "PAYMENT_DECLINED",
        "title": {
            "fa": "پرداخت رد شده",
            "en": "payment declined"
        }
    }

    items = {
        "UNPAID": UNPAID,
        "PAYMENT_CHECK": PAYMENT_CHECK,
        "ACCEPTED": ACCEPTED,
        "PREPARATION": PREPARATION,
        "SENT": SENT,
        "DECLINED": DECLINED,
        "PAYMENT_DECLINED": PAYMENT_DECLINED,
    }
