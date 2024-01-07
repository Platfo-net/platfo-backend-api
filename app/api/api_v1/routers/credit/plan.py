from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.role import Role

router = APIRouter(prefix='/plans')


@router.get('/all')
def get_plans(
    *,
    db: Session = Depends(deps.get_db),
    module: str = None,
    currency: str,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    plans = services.credit.plan.get_multi(db, currency=currency, module=module)

    plans_out = []

    for plan in plans:
        features = [
            schemas.credit.Feature(
                id=feature.uuid,
                title=feature.title,
                description=feature.description,
            )
            for feature in plan.features
        ]
        plans_out.append(
            schemas.credit.DetailedPlan(
                id=plan.uuid,
                title=plan.title,
                description=plan.description,
                features=features,
                extend_days=plan.extend_days,
                extend_count=plan.extend_count,
                original_price=plan.original_price,
                discounted_price=plan.discounted_price,
                currency=plan.currency,
                discount_percentage=int((plan.original_price - plan.discounted_price)/plan.original_price),
                module=plan.module,
            )
        )
    return plans_out
