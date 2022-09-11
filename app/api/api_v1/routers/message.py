from typing import List
from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

router = APIRouter(prefix="/message", tags=["Messages"])


@router.get("/archive/{page_id}/{contact_igs_id}",
            response_model=List[schemas.Message])
def get_archive(
    *,
    db: Session = Depends(deps.get_db),
    contact_igs_id: str,
    page_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):

    messages = services.message.get_pages_messages(
        db,
        contact_igs_id=contact_igs_id,
        page_id=page_id,
        skip=skip,
        limit=limit
    )

    return [

        schemas.Message(
            id=message.id,
            from_page_id=message.from_page_id,
            to_page_id=message.to_page_id,
            content=message.content,
            user_id=message.user_id,
            send_at=message.send_at
        ) for message in messages if len(messages) > 0
    ]
