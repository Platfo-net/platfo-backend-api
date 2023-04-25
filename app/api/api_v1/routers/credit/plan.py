

from app import services, schemas
from fastapi import APIRouter, Depends, Security
from app import models
from app.api import deps
from app.constants.role import Role
from sqlalchemy.orm import Session

router = APIRouter(prefix="/plans")


@router.get("/")
def get_plans(
        *,
        db: Session = Depends(deps.get_db),
        module: str = None,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    plans = services.credit.plan.get_multi(db, module=module)

    plans_out = []

    for plan in plans:
        features = [schemas.credit.Feature(
            id=feature.uuid,
            title=feature.title,
            description=feature.description,
        ) for feature in plan.features
        ]
        plans_out.append(
            schemas.credit.Plan(
                id=plan.uuid,
                title=plan.title,
                description=plan.description,
                features=features,
                extend_days=plan.extend_days,
                extend_count=plan.extend_count,
            )
        )
    return plans_out
