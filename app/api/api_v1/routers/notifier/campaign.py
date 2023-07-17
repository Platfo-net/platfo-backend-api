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
    pagination, items = services.notifier.campaign.get_multi(
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
                group_name=item.group_name,
                image=image,
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
    group = services.notifier.group.get_by_uuid(db, obj_in.group_id)

    if not group:
        raise_http_exception(Error.GROUP_NOT_FOUND)
    if not group.user_id == current_user.id:
        raise_http_exception(Error.GROUP_NOT_FOUND_ACCESS_DENIED)

    if not group.facebook_page_id == obj_in.facebook_page_id:
        raise_http_exception(Error.GROUP_DOES_NOT_BELONGS_TO_THIS_PAGE)

    campaign_obj = schemas.notifier.CampaignCreate(
        name=obj_in.name,
        description=obj_in.description,
        facebook_page_id=obj_in.facebook_page_id,
        is_draft=obj_in.is_draft,
        content=obj_in.content,
        group_name=group.name,
        image=obj_in.image,
    )

    campaign = services.notifier.campaign.create(
        db, obj_in=campaign_obj, user_id=current_user.id
    )

    group_contacts = services.notifier.group_contact.get_by_group(db, group_id=group.id)
    contacts = []
    for contact in group_contacts:
        contacts.append(
            schemas.notifier.CampaignContactCreate(
                contact_id=contact.contact_id, contact_igs_id=contact.contact_igs_id
            )
        )

    services.notifier.campaign_contact.create_bulk(
        db, campaign_id=campaign.id, contacts=contacts
    )
    image = storage.get_file(campaign.image, settings.S3_CAMPAIGN_BUCKET)

    return schemas.notifier.Campaign(
        id=campaign.uuid,
        name=campaign.name,
        description=campaign.description,
        created_at=campaign.created_at,
        is_draft=campaign.is_draft,
        status=campaign.status,
        group_name=group.name,
        image=image,
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

    if db_obj.is_draft is False:
        raise_http_exception(Error.CAMPAIGN_ALREADY_ACTIVE)
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
        ),
    )
    image = storage.get_file(obj_in.image, settings.S3_CAMPAIGN_BUCKET)
    return schemas.notifier.CampaignUpdate(
        name=campaign.name,
        description=campaign.description,
        content=campaign.content,
        is_draft=campaign.is_draft,
        image=image,
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

    sent_count = services.notifier.campaign_contact.get_all_sent_count(db, campaign.id)
    seen_count = services.notifier.campaign_contact.get_all_seen_count(db, campaign.id)
    contact_count = services.notifier.campaign_contact.get_all_contacts_count(
        db, campaign.id
    )
    instagram_page = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=campaign.facebook_page_id
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
        group_name=campaign.group_name,
        content=campaign.content,
        user_id=current_user.uuid,
        facebook_page_id=campaign.facebook_page_id,
        account=account,
        sent_count=sent_count,
        seen_count=seen_count,
        total_contact_count=contact_count,
        image=image,
    )


@router.get('/{id}/contacts')
def get_campain_contacts(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    page: int = 1,
    page_size: int = 20,
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
    if not campaign.id == current_user.id:
        raise_http_exception(Error.CAMPAIGN_NOT_FOUND_ACCESS_DENIED)

    (
        campaign_contacts,
        pagination,
    ) = services.notifier.campaign_contact.get_campain_contacts(
        db, campaign_id=campaign.id, page=page, page_size=page_size
    )
    contacts = []
    for contact in campaign_contacts:
        contacts.append(
            schemas.notifier.ContactSample(
                profile_image=contact.contact.information.get('profile_image'),
                username=contact.contact.information.get('username'),
            )
        )
    return schemas.notifier.CampaignContactApiSchema(
        items=contacts, pagination=pagination
    )


@router.get('/activate/{id}')
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
