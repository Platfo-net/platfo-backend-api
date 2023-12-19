from sqlalchemy.orm import Session

from app import models, schemas
from app.services.base import BaseServices


class TaskResultServices(
    BaseServices[
        models.monitoring.TaskResult,
        schemas.monitoring.TaskResultCreate,
    ]
):
    def create(
            self,
            db: Session,
            *,
            obj_in: schemas.monitoring.TaskResultCreate,
    ):
        db_obj = self.model(function_name=obj_in.function_name,
                            stacktrace=obj_in.stacktrace,
                            is_successful=obj_in.is_successful)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)


task_result = TaskResultServices(models.monitoring.TaskResult)
