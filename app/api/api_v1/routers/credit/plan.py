from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/plans')


@router.get('/')
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
                discount_percentage=plan.discounted_price,
                is_discounted=plan.is_discounted,
                module=plan.module,
            )
        )
    return plans_out


@router.get('/{id}')
def get_plan(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4 = None,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
        ],
    ),
):
    plan = services.credit.plan.get_by_uuid(db, uuid=id)
    if not plan:
        raise raise_http_exception(Error.PLAN_NOT_FOUND)

    features = [
        schemas.credit.Feature(
            id=feature.uuid,
            title=feature.title,
            description=feature.description,
        )
        for feature in plan.features
    ]
    return schemas.credit.DetailedPlan(
        id=plan.uuid,
        title=plan.title,
        description=plan.description,
        features=features,
        extend_days=plan.extend_days,
        extend_count=plan.extend_count,
        currency=plan.currency,
        original_price=plan.original_price,
        discounted_price=plan.discounted_price,
        discount_percentage=plan.discount_percentage,
        is_discounted=plan.is_discounted,
    )
