from typing import Any, List
from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session


router = APIRouter(prefix="/trigger", tags=["Trigger"])


@router.get("/all", response_model=List[schemas.Trigger])
def get_list_of_triggers(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
        ],
    ),
) -> Any:

    return services.trigger.get_multi(db, skip=skip, limit=limit)
