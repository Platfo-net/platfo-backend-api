from typing import Any, List

from fastapi import APIRouter, Depends, Security
from fastapi.exceptions import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.constants.application import Application
from app.constants.platform import Platform



router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/all", response_model=List[schemas.Account])
def get_accounts_list(
        *,
        db: Session = Depends(deps.get_db),
        platform: str = None,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
) -> Any:
    """
        Get list of accounts from different platforms
    """
    instagram_pages = services.instagram_page.get_multi_by_user_id(
        db, user_id=current_user.id
    )

    accounts = [
        schemas.Account(
            id=item.id,
            username=item.instagram_username,
            profile_image=item.instagram_profile_picture_url,
            platform=Platform.INSTAGRAM["name"],
            page_id=item.facebook_page_id,
        )
        for item in instagram_pages if len(instagram_pages) > 0
    ]
    return accounts


@router.get("/{id}", response_model=schemas.InstagramPage)
def get_account(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
) -> Any:
    """
        Get list of accounts from different platforms
    """
    instagram_page = services.instagram_page.get(db, id)
    if not instagram_page:
        raise HTTPException(
            status_code=Error.ACCOUNT_NOT_FOUND["status_code"],
            detail=Error.ACCOUNT_NOT_FOUND["text"],
        )

    return instagram_page


@router.delete("/{id}")
def delete_account(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
) -> Any:
    instagram_page = services.instagram_page.get(db, id)

    if not instagram_page:
        raise HTTPException(
            status_code=Error.ACCOUNT_NOT_FOUND["status_code"],
            detail=Error.ACCOUNT_NOT_FOUND["text"],
        )

    services.instagram_page.remove(db, id=id)

    services.contact.remove_by_user_page_id(
        db, user_page_id=instagram_page.facebook_page_id)
    services.message.remove_by_user_page_id(
        db, user_page_id=instagram_page.facebook_page_id)
    connections = services.connection.get_page_connection(
        db,
        account_id=instagram_page.id,
        application_name=Application.BOT_BUILDER["name"]
    )

    for connection in connections:
        services.connection_chatflow.remove_by_connection_id_accounts(
            db,
            connection_id=connection.id
        )
        services.connection.remove(db, id=connection.id)

    return
