from typing import Any, List

from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from redis.client import Redis
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.application import Application
from app.constants.errors import Error
from app.constants.platform import Platform
from app.constants.role import Role
from app.core.cache import remove_data_from_cache
from app.core.exception import raise_http_exception

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/all", response_model=List[schemas.Account])
def get_accounts_list(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    instagram_pages = services.instagram_page.get_multi_by_user_id(
        db, user_id=current_user.id
    )

    accounts = [
        schemas.Account(
            id=item.uuid,
            username=item.username,
            profile_image=item.profile_picture_url,
            platform=Platform.INSTAGRAM["name"],
            facebook_page_id=item.facebook_page_id,
        )
        for item in instagram_pages
        if len(instagram_pages) > 0
    ]
    return accounts


@router.get("/{id}", response_model=schemas.AccountDetail)
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
    instagram_page = services.instagram_page.get_by_uuid(db, uuid=id)
    if not instagram_page:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)
    if instagram_page.user_id != current_user.id:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)
    return schemas.AccountDetail(
        id=instagram_page.uuid,
        facebook_page_id=instagram_page.facebook_page_id,
        username=instagram_page.username,
        profile_image=instagram_page.profile_picture_url,
        information=instagram_page.information,
        platform=Platform.INSTAGRAM["name"],
    )


@router.delete("/{id}")
def delete_account(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client),
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    instagram_page = services.instagram_page.get_by_uuid(db, id)

    if not instagram_page:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)
    if instagram_page.user_id != current_user.id:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    remove_data_from_cache(redis_client, instagram_page.instagram_page_id)

    services.instagram_page.remove(db, id=id)

    services.live_chat.contact.remove_by_user_page_id(
        db, user_page_id=instagram_page.facebook_page_id
    )
    services.live_chat.message.remove_by_user_page_id(
        db, user_page_id=instagram_page.facebook_page_id
    )
    connections = services.connection.get_page_connections(
        db,
        account_id=instagram_page.id,
        application_name=Application.BOT_BUILDER,
    )

    for connection in connections:
        services.connection.remove(db, id=connection.id)

    return
