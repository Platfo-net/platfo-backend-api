from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.platform import Platform
from app.constants.role import Role
from app.core import storage
from app.core.config import settings
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/campaign')


@router.get('/all', response_model=schemas.notifier.CampaignListApi)
def get_all_user_campaigns(
    *,
    db: Session = Depends(deps.get_db),
    page: int = 1,
    page_size: int = 20,
    facebook_page_id: int = None,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    items, pagination = services.notifier.campaign.get_multi(
        db,
        user_id=current_user.id,
        facebook_page_id=facebook_page_id,
        page=page,
        page_size=page_size,
    )

    campaigns = []
    for item in items:
        image = storage.get_file(item.image, settings.S3_CAMPAIGN_BUCKET)
        campaigns.append(
            schemas.notifier.Campaign(
                id=item.uuid,
                name=item.name,
                description=item.description,
                created_at=item.created_at,
                status=item.status,
                is_draft=item.is_draft,
                image=image,
                leads_criteria=item.leads_criteria,
            )
        )

    return schemas.notifier.CampaignListApi(
        items=campaigns,
        pagination=pagination,
    )


@router.post('/', response_model=schemas.notifier.Campaign)
def create_campaign(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.notifier.CampaignCreateApiSchema,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):

    campaign_obj = schemas.notifier.CampaignCreate(
        name=obj_in.name,
        description=obj_in.description,
        facebook_page_id=obj_in.facebook_page_id,
        is_draft=obj_in.is_draft,
        content=obj_in.content,
        image=obj_in.image,
        leads_criteria=obj_in.leads_criteria,
    )

    campaign = services.notifier.campaign.create(
        db, obj_in=campaign_obj, user_id=current_user.id
    )

    image = storage.get_file(campaign.image, settings.S3_CAMPAIGN_BUCKET)

    return schemas.notifier.Campaign(
        id=campaign.uuid,
        name=campaign.name,
        description=campaign.description,
        created_at=campaign.created_at,
        is_draft=campaign.is_draft,
        status=campaign.status,
        image=image,
        leads_criteria=obj_in.leads_criteria,
    )


@router.put('/{id}', response_model=schemas.notifier.CampaignUpdate)
def update_campaign(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    obj_in: schemas.notifier.CampaignUpdate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    db_obj = services.notifier.campaign.get_by_uuid(db, id)

    campaign = services.notifier.campaign.update(
        db,
        db_obj=db_obj,
        user_id=current_user.id,
        obj_in=schemas.notifier.CampaignUpdate(
            name=obj_in.name,
            description=obj_in.description,
            content=obj_in.content,
            is_draft=obj_in.is_draft,
            image=obj_in.image,
            leads_criteria=obj_in.leads_criteria,
        ),
    )
    image = storage.get_file(obj_in.image, settings.S3_CAMPAIGN_BUCKET)
    return schemas.notifier.Campaign(
        id=campaign.uuid,
        name=campaign.name,
        description=campaign.description,
        content=campaign.content,
        is_draft=campaign.is_draft,
        image=image,
        leads_criteria=campaign.leads_criteria
    )


@router.get('/{id}', response_model=schemas.notifier.CampaignDetail)
def get_campaign_by_id(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    campaign = services.notifier.campaign.get_by_uuid(db, id)
    if not campaign:
        raise_http_exception(Error.CAMPAIGN_NOT_FOUND)

    instagram_page = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=campaign.facebook_page_id
    )
    if not instagram_page:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    sent_count = services.notifier.campaign_lead.get_all_sent_count(db, campaign.id)
    seen_count = services.notifier.campaign_lead.get_all_seen_count(db, campaign.id)
    lead_count = services.notifier.campaign_lead.get_all_leads_count(
        db, campaign.id
    )
    account = schemas.Account(
        id=instagram_page.uuid,
        username=instagram_page.username,
        profile_image=instagram_page.profile_picture_url,
        platform=Platform.INSTAGRAM['name'],
        page_id=instagram_page.facebook_page_id,
    )
    image = storage.get_file(campaign.image, settings.S3_CAMPAIGN_BUCKET)
    return schemas.notifier.CampaignDetail(
        id=campaign.uuid,
        name=campaign.name,
        description=campaign.description,
        created_at=campaign.created_at,
        is_draft=campaign.is_draft,
        status=campaign.status,
        content=campaign.content,
        user_id=current_user.uuid,
        facebook_page_id=campaign.facebook_page_id,
        account=account,
        sent_count=sent_count,
        seen_count=seen_count,
        total_lead_count=lead_count,
        image=image,
    )


@router.get('/{id}/activate')
def change_campaign_is_draft(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    is_draft: bool,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    campaign = services.notifier.campaign.get_by_uuid(db, id)

    if not campaign:
        raise_http_exception(Error.CAMPAIGN_NOT_FOUND)
    if not campaign.user_id == current_user.id:
        raise_http_exception(Error.CAMPAIGN_NOT_FOUND_ACCESS_DENIED)

    services.notifier.campaign.change_is_draft(db, db_obj=campaign, is_draft=is_draft)
    return
