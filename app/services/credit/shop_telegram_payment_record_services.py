from app import models
from sqlalchemy.orm import Session

class ShopTelegramPaymentRecordServices:
    def __init__(self, model):
        self.model: models.credit.ShopCredit = model
        
    def create(self, db:Session , * , shop_id:int ,plan_id : int , reply_to_message_id : int ):
        db_obj = self.model(
            shop_id = shop_id , 
            plan_id = plan_id,
            
        )


shop_telegram_payment_record = ShopTelegramPaymentRecordServices(
    models.credit.CreditShopTelegramPaymentRecord)
