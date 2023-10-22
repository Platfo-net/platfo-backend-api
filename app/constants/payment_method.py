
from pydantic import BaseModel


class CardTransferValidationSchema(BaseModel):
    card_number: str
    name: str
    bank: str


class PaymentMethod:
    CARD_TRANSFER = {
        "title": "Card Transfer",
        "fa" : "کارت به کارت",
        "description": "",
        "information_fields": {
            "Card Number": True,
            "Name": True,
            "Bank": False,
        },
        "payment_fields": {
            "Payment Tracking Number": True,
            "Payment Datetime": False,
            "Receipt Image": False,
        },
        "validation_schema": CardTransferValidationSchema
    }

    items = {
        "Card Transfer": CARD_TRANSFER
    }
