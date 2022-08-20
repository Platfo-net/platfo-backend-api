from typing import Any, List

from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from app.constants.role import Role
from app.constants.platform import Platform
from app.constants.application import Application


router = APIRouter(prefix="/constants", tags=["Constant"])


@router.get("/roles", response_model=List[schemas.Role])
def get_roles(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    admin = services.role.get_by_name(db, name=Role.ADMIN["name"])
    user = services.role.get_by_name(db, name=Role.USER["name"])
    return [user, admin]


@router.get("/platforms")
def get_platforms(
    db: Session = Depends(deps.get_db)
) -> Any:

    return [{"name": Platform.INSTAGRAM["name"]}]


@router.get("/applications")
def get_applications(
    db: Session = Depends(deps.get_db)
) -> Any:
    return [{"name": Application.BOT_BUILDER["name"]}]
