from typing import Any, List
from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session


router = APIRouter(prefix="/trigger", tags=["triggers"])


@router.get("/all", response_model=List[schemas.Trigger])
def get_all_triggers(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    return services.trigger.get_multi(db, skip=skip, limit=limit)


@router.post("", response_model=schemas.Trigger)
def create_trigger(
    *,
    db: Session = Depends(deps.get_db),
    trigger_in: schemas.TriggerCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    trigger = services.trigger.create(db, obj_in=trigger_in)
    return trigger
