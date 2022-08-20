from app.services.base import BaseService
from app import models, schemas


class PlanService(
    BaseService
    [
        models.Plan,
        schemas.PlanCreate,
        schemas.PlanUpdate
    ]
):
    pass


plan = PlanService(models.Plan)
