from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session


router = APIRouter(prefix="/campign")


@router.get("/all", status_code=status.HTTP_201_CREATED)
def get_all_user_campaigns(
    *,
    db: Session = Depends(deps.get_db),
    page: int = 1,
    page_size: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    pagination, items = services.postman.campaign.get_multi(
        db, user_id=current_user.id, page=page, page_size=page_size)

    campaigns = []
    for item in items:
        campaigns.append(
            schemas.postman.Campaign(
                name=item.name,
                description=item.description,
                created_at=item.created_at,
                status=item.status,
                is_draft=item.is_draft,
            ))

    return schemas.postman.CampaignListApi(
        pagination=pagination,
        items=campaigns
    )
