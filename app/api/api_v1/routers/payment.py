from typing import Any

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from app.constants.transaction_status import TransactionStatus


router = APIRouter(prefix="/payment", tags=["Payment"])


@router.post("/transaction", status_code=status.HTTP_201_CREATED)
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.TransactionCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    if obj_in not in TransactionStatus.VALID_STATUS:
        raise HTTPException(
            status_code=Error.INVALID_TRANSACTION_STATUS['status_code'],
            detail=Error.INVALID_TRANSACTION_STATUS['text']
        )

    services.transaction.create(db, obj_in=obj_in, user_id=current_user.id)

    if obj_in.status == TransactionStatus.SUCCESS["value"]:
        credit = services.credit.get_by_user_id(db, user_id=current_user.id)
        plan = services.plan.get(db, id=obj_in.plan_id)
        if not credit:
            credit = services.credit.create(db, user_id=current_user.id)

        services.credit.add_days_to_credit(
            db, user_id=credit.user_id, days_add=plan.days_add)
