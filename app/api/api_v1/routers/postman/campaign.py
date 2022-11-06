from pydantic import UUID4

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.platform import Platform
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security, status, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/campaign")


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
                group_name=item.group_name
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

    campaign = services.postman.campaign.create(
        db,
        obj_in=campaign_obj,
        user_id=current_user.id
    )

    group = services.postman.group.get(db, id=obj_in.group_id)
    services.postman.campaign.set_group_name(
        db, campaign_id=campaign.id, group_name=group.name)

    group_contacts = services.postman.group_contact.get_by_group(db, group_id=group.id)
    contacts = []
    for ele in group_contacts:
        contacts.append(schemas.postman.CampaignContactCreate(
            contact_id=ele.contact_id,
            contact_igs_id=ele.contact_igs_id
        ))
    services.postman.campaign_contact.create_bulk(
        db,
        campaign_id=campaign.id,
        contacts=contacts
    )

    return schemas.postman.Campaign(
        name=campaign.name,
        description=campaign.description,
        created_at=campaign.created_at,
        is_draft=campaign.is_draft,
        status=campaign.status,
        group_name=group.name
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
    db_obj = services.postman.campaign.get(db, campaign_id=id)

    if db_obj.is_draft is False:
        raise HTTPException(
            status_code=Error.CAMPAIGN_ALREADY_ACTIVE['status'],
            detail=Error.CAMPAIGN_ALREADY_ACTIVE['text']
        )
    campaign = services.postman.campaign.update(
        db,
        db_obj=db_obj,
        user_id=current_user.id,
        obj_in=schemas.postman.CampaignUpdate(
            name=obj_in.name,
            description=obj_in.description,
            content=obj_in.content,
            is_draft=obj_in.is_draft
        ),
    )
    return schemas.postman.CampaignUpdate(
        name=campaign.name,
        description=campaign.description,
        content=campaign.content,
        is_draft=campaign.is_draft
    )


@router.get("/{id}")
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
    campaign, campaign_contacts, sent_count,\
        seen_count, total_contact_count = services.postman.campaign.\
        get_by_detail(db, campaign_id=id)
    contacts_id = []
    for campaign_contact in campaign_contacts:
        contacts_id.append(campaign_contact.contact_id)
    contacts = services.live_chat.contact.get_bulk(db, contacts_id=contacts_id)
    instagram_page = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=campaign.facebook_page_id
    )

    account = schemas.Account(
        id=instagram_page.id,
        username=instagram_page.username,
        profile_image=instagram_page.profile_picture_url,
        platform=Platform.INSTAGRAM["name"],
        page_id=instagram_page.facebook_page_id
    )
    return schemas.postman.CampaignDetail(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        created_at=campaign.created_at,
        is_draft=campaign.is_draft,
        status=campaign.status,
        group_name=campaign.group_name,
        content=campaign.content,
        user_id=campaign.user_id,
        facebook_page_id=campaign.facebook_page_id,
        contacts=contacts,
        account=account,
        sent_count=sent_count,
        seen_count=seen_count,
        total_contact_count=total_contact_count
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
    campaign = services.postman.campaign.get(db, campaign_id=id)
    if not campaign:
        raise HTTPException(
            status_code=Error.CAMPAIGN_NOT_FOUND['status'],
            detail=Error.CAMPAIGN_NOT_FOUND['text']
        )

    services.postman.campaign.change_is_draft(
        db,
        campaign_id=campaign.id,
        is_draft=is_draft
    )
    return
