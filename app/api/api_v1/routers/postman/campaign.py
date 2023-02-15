from pydantic import UUID4

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.platform import Platform
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/campaign")


@router.get("/all", response_model=schemas.postman.CampaignListApi)
def get_all_user_campaigns(
        *,
        db: Session = Depends(deps.get_db),
        page: int = 1,
        page_size: int = 20,
        facebook_page_id: int = None,
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
        page_size=page_size,
    )

    campaigns = []
    for item in items:
        campaigns.append(
            schemas.postman.Campaign(
                id=item.uuid,
                name=item.name,
                description=item.description,
                created_at=item.created_at,
                status=item.status,
                is_draft=item.is_draft,
                group_name=item.group_name,
            )
        )

    return schemas.postman.CampaignListApi(
        items=campaigns,
        pagination=pagination,
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
        ),
):
    group = services.postman.group.get_by_uuid(db, obj_in.group_id)

    if not group:
        raise HTTPException(
            status_code=Error.GROUP_NOT_FOUND["status_code"],
            detail=Error.GROUP_NOT_FOUND["text"],
        )
    if not group.user_id == current_user.id:
        raise HTTPException(
            status_code=Error.GROUP_NOT_FOUND["status_code"],
            detail=Error.GROUP_NOT_FOUND["text"],
        )
    if not group.facebook_page_id == obj_in.facebook_page_id:
        raise HTTPException(
            status_code=Error.GROUP_DOES_NOT_BELONGS_TO_THIS_PAGE["status_code"],
            detail=Error.GROUP_DOES_NOT_BELONGS_TO_THIS_PAGE["text"],
        )
    campaign_obj = schemas.postman.CampaignCreate(
        name=obj_in.name,
        description=obj_in.description,
        facebook_page_id=obj_in.facebook_page_id,
        is_draft=obj_in.is_draft,
        content=obj_in.content,
        group_name=group.name
    )

    campaign = services.postman.campaign.create(
        db, obj_in=campaign_obj, user_id=current_user.id
    )

    group_contacts = services.postman.group_contact.get_by_group(db, group_id=group.id)
    contacts = []
    for contact in group_contacts:
        contacts.append(
            schemas.postman.CampaignContactCreate(
                contact_id=contact.contact_id,
                contact_igs_id=contact.contact_igs_id
            )
        )

    services.postman.campaign_contact.create_bulk(
        db, campaign_id=campaign.id, contacts=contacts
    )

    return schemas.postman.Campaign(
        id=campaign.uuid,
        name=campaign.name,
        description=campaign.description,
        created_at=campaign.created_at,
        is_draft=campaign.is_draft,
        status=campaign.status,
        group_name=group.name,
    )


@router.put("/{id}", response_model=schemas.postman.CampaignUpdate)
def update_campaign(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        obj_in: schemas.postman.CampaignUpdate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    db_obj = services.postman.campaign.get_by_uuid(db, id)

    if db_obj.is_draft is False:
        raise HTTPException(
            status_code=Error.CAMPAIGN_ALREADY_ACTIVE["status"],
            detail=Error.CAMPAIGN_ALREADY_ACTIVE["text"],
        )
    campaign = services.postman.campaign.update(
        db,
        db_obj=db_obj,
        user_id=current_user.id,
        obj_in=schemas.postman.CampaignUpdate(
            name=obj_in.name,
            description=obj_in.description,
            content=obj_in.content,
            is_draft=obj_in.is_draft,
        ),
    )
    return schemas.postman.CampaignUpdate(
        name=campaign.name,
        description=campaign.description,
        content=campaign.content,
        is_draft=campaign.is_draft,
    )


@router.get("/{id}", response_model=schemas.postman.CampaignDetail)
def get_campaign_by_id(
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
):
    campaign = services.postman.campaign.get_by_uuid(db, id)
    if not campaign:
        raise HTTPException(
            status_code=Error.CAMPAIGN_NOT_FOUND["status"],
            detail=Error.CAMPAIGN_NOT_FOUND["text"]
        )
    (
        campaign,
        sent_count,
        seen_count,
        total_contact_count,
    ) = services.postman.campaign.get_by_detail(db, campaign.id)
    instagram_page = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=campaign.facebook_page_id
    )

    account = schemas.Account(
        id=instagram_page.uuid,
        username=instagram_page.username,
        profile_image=instagram_page.profile_picture_url,
        platform=Platform.INSTAGRAM["name"],
        page_id=instagram_page.facebook_page_id,
    )
    return schemas.postman.CampaignDetail(
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
        total_contact_count=total_contact_count,
    )


@router.get("/{id}/contacts")
def get_campain_contacts(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
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
    campaign = services.postman.campaign.get_by_uuid(db, id)
    if not campaign:
        raise HTTPException(
            status_code=Error.CAMPAIGN_NOT_FOUND["status"],
            detail=Error.CAMPAIGN_NOT_FOUND["text"]
        )
    campaign_contacts, pagination = services.postman.campaign_contact.get_campain_contacts(
        db, campaign_id=campaign.id, page=page, page_size=page_size
    )
    contacts = []
    for contact in campaign_contacts:
        contacts.append(schemas.postman.ContactSample(
            profile_image=contact.contact.information.get("profile_image"),
            username=contact.contact.information.get("username")
        ))
    return schemas.postman.CampaignContactApiSchema(
        items=contacts,
        pagination=pagination
    )


@router.get("/activate/{id}")
def change_campaign_is_draft(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        is_draft: bool,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
):
    campaign = services.postman.campaign.get_by_uuid(db, id)

    if not campaign:
        raise HTTPException(
            status_code=Error.CAMPAIGN_NOT_FOUND["status"],
            detail=Error.CAMPAIGN_NOT_FOUND["text"],
        )
    if not campaign.user_id == current_user.id:
        raise HTTPException(
            status_code=Error.CAMPAIGN_NOT_FOUND["status"],
            detail=Error.CAMPAIGN_NOT_FOUND["text"],
        )

    services.postman.campaign.change_is_draft(
        db, db_obj=campaign, is_draft=is_draft
    )
    return
