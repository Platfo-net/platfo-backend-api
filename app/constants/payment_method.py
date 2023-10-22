
from pydantic import BaseModel


class CardTransferValidationSchema(BaseModel):
    card_number: str
    name: str
    bank: str


class PaymentMethod:
    CARD_TRANSFER = {
        "title": "Card Transfer",
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
        "CARD_TRANSFER": CARD_TRANSFER
    }
