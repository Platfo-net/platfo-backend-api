from app.services.base import BaseServices
from app import models, schemas


class PlanServices(
    BaseServices
    [
        models.Plan,
        schemas.PlanCreate,
        schemas.PlanUpdate
    ]
):
    pass


plan = PlanServices(models.Plan)
