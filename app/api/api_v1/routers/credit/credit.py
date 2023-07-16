from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.role import Role

router = APIRouter(prefix='/credit')


@router.get('', response_model=schemas.credit.Invoice)
def get_user_credit(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    credits = services.credit.credit.get_by_user(db, uuid=id, user_id=current_user.id)

    return [
        schemas.credit.Credit(
            module=credit.module,
            count=credit.count,
            expires_at=credit.expires_at
        )
        for credit in credits
    ]
