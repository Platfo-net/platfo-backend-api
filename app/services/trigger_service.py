from app.services.base import BaseService
from app import models, schemas
from sqlalchemy.orm import Session

class TriggerService(
        BaseService[
            schemas.Trigger,
            schemas.TriggerCreate,
            schemas.TriggerUpdate
        ]):
    def get_by_name(self,db:Session , name:str)->schemas.Trigger:
        return db.query(self.model).filter(self.model.name == name).first()    

trigger = TriggerService(models.Trigger)
