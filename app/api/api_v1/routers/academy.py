from typing import Any, List
from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session


router = APIRouter(prefix="/academy", tags=["Academy"])


@router.get("/category/all", response_model=List[schemas.Category])
def get_categories_list(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
) -> Any:
    services.academy.category.get_multi
    pass