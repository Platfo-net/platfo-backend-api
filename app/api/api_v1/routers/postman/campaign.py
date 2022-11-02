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
    facebook_page_id: str = None,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    pagination, items = services.postman.campaign.get_multi(
        db,
        user_id=current_user.id,
        facebook_page_id=facebook_page_id,
        page=page,
        page_size=page_size
    )

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


@router.post("/", response_model=schemas.postman.Campaign)
def create_campaign(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.postman.CampaignCreateApiSchema,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    )
):
    campaign_obj = schemas.postman.CampaignCreate(
        name=obj_in.name,
        description=obj_in.description,
        facebook_page_id=obj_in.facebook_page_id,
        is_draft=obj_in.is_draft,
        content=obj_in.content,
    )

    campaign = services.postman.campaign.create(db, obj_in=campaign_obj)
    group = services.postman.group.get(db, id=obj_in.group_id)
    services.postman.campaign.set_group_name(
        db, campaign_id=campaign.id, group_name=group.name)

    services.postman.campaign_contact.create_bulk(db, contacts=obj_in.contacts)

    return schemas.postman.Campaign(
        name=campaign.name,
        description=campaign.description,
        created_at=campaign.created_at,
        is_draft=campaign.is_draft,
        status=campaign.status,
        group_name=group.name
    )





@router.post("/", response_model=schemas.postman.Campaign)
def create_campaign(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.postman.CampaignCreateApiSchema,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    )
):
    campaign_obj = schemas.postman.CampaignCreate(
        name=obj_in.name,
        description=obj_in.description,
        facebook_page_id=obj_in.facebook_page_id,
        is_draft=obj_in.is_draft,
        content=obj_in.content,
    )

    campaign = services.postman.campaign.create(db, obj_in=campaign_obj)
    group = services.postman.group.get(db, id=obj_in.group_id)
    services.postman.campaign.set_group_name(
        db, campaign_id=campaign.id, group_name=group.name)

    services.postman.campaign_contact.create_bulk(db, contacts=obj_in.contacts)

    return schemas.postman.Campaign(
        name=campaign.name,
        description=campaign.description,
        created_at=campaign.created_at,
        is_draft=campaign.is_draft,
        status=campaign.status,
        group_name=group.name
    )


