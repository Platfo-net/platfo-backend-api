from typing import Any, List
from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session


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
        db, user_id=current_user.id)
    accounts = [
        schemas.Account(
            id=item.id,
            username=item.instagram_username,
            profile_image_url=item.instagram_profile_picture_url,
            platform="instagram",
            page_id=item.facebook_page_id
        )
        for item in instagram_pages if len(instagram_pages) > 0
    ]
    return accounts
