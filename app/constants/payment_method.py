from pydantic import BaseModel


class CardTransferValidationSchema(BaseModel):
    card_number: str
    name: str
    bank: str


class OnSpotValidationSchema(BaseModel):
    pass


class ZarrinPalValidationSchema(BaseModel):
    merchant_id: str


class PaymentMethod:
    CARD_TRANSFER = {
        "title": "Card Transfer",
        "fa": "کارت به کارت",
        "description": "",
        "information_fields": {
            "card_number": True,
            "name": True,
            "bank": False,
        },
        "payment_fields": {
            "payment_tracking_number": True,
            "payment_datetime": False,
            "receipt_image": False,
        },
        "validation_schema": CardTransferValidationSchema,
    }

    ON_SPOT = {
        "title": "On Spot",
        "fa": "پرداخت در محل",
        "description": "",
        "information_fields": {},
        "payment_fields": {},
        "validation_schema": OnSpotValidationSchema,
    }

    ZARRIN_PAL = {
        "title": "Zarrin Pal",
        "fa": "پرداخت از طریق درگاه زرین پال",
        "description": "",
        "information_fields": {
            "merchant_id": True,
        },
        "payment_fields": {
            "ref_id": True,
        },
        "validation_schema": None,
    }

    items = {
        "Card Transfer": CARD_TRANSFER,
        "On Spot": ON_SPOT,
        "Zarrin Pal": ZARRIN_PAL,
    }

    payment_gateway_items = [ZARRIN_PAL["title"]]
