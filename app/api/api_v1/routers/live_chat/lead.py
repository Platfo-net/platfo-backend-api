from datetime import date

from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/lead')


@router.get('/{id}', response_model=schemas.live_chat.Lead)
def get_lead(
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
    """
        Api for getting and specific lead data

    Args:

        id (UUID4): id of lead in system:
                eg: 3c8f64ca-f1b0-4692-9833-232c4b560d2f

    Raises:

        HTTPException 404: when lead not found

    """

    lead = services.live_chat.lead.get_by_uuid(db, id)

    if not lead:
        raise_http_exception(Error.LEAD_NOT_FOUND)

    return schemas.live_chat.Lead(
        lead_igs_id=lead.lead_igs_id,
        facebook_page_id=lead.facebook_page_id,
        user_id=lead.user_id,
        id=lead.uuid,
        last_message_at=lead.last_message_at,
        last_interaction_at=lead.last_interaction_at,
        last_message=lead.last_message,
        username=lead.username,
        profile_image=lead.profile_image,
        name=lead.name,
        followers_count=lead.followers_count,
        is_verified_user=lead.is_verified_user,
        is_user_follow_business=lead.is_user_follow_business,
        is_business_follow_user=lead.is_business_follow_user,

    )


@router.put('/{page_id}', deprecated=True)
def update_page_leads_information(
    *,
    db: Session = Depends(deps.get_db),
    lead_igs_id: str,
    obj_in: schemas.live_chat.ProfileUpdate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    data = dict()
    data[obj_in.key] = obj_in.value
    leads = services.live_chat.lead.update_information(
        db, lead_igs_id=lead_igs_id, data=data
    )

    return leads


@router.post('/all/{facebook_page_id}', response_model=schemas.live_chat.LeadList)
def get_all_lead_based_on_filters(
    *,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(deps.get_db),
    facebook_page_id: int,
    from_date: date = None,
    is_user_follow_business: bool = None,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    account = services.instagram_page.get_by_facebook_page_id(
        db, facebook_page_id=facebook_page_id
    )
    if account.user_id != current_user.id:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    if not account:
        raise_http_exception(Error.ACCOUNT_NOT_FOUND)

    leads, pagination = services.live_chat.lead.get_multi(
        db=db,
        facebook_page_id=facebook_page_id,
        is_user_follow_business=is_user_follow_business,
        from_date=from_date,
        page=page,
        page_size=page_size,
    )

    if not leads:
        return schemas.live_chat.LeadList(
            items=[],
            pagination=schemas.Pagination(),
        )

    leads = [
        schemas.live_chat.Lead(
            lead_igs_id=lead.lead_igs_id,
            facebook_page_id=lead.facebook_page_id,
            id=lead.uuid,
            last_message_at=lead.last_message_at,
            last_interaction_at=lead.last_interaction_at,
            last_message=lead.last_message,
            first_impression=lead.first_impression,
            profile_image=lead.profile_image,
            username=lead.username,
            name=lead.name,
            followers_count=lead.followers_count,
            is_verified_user=lead.is_verified_user,
            is_user_follow_business=lead.is_user_follow_business,
            is_business_follow_user=lead.is_business_follow_user,

        )
        for lead in leads
    ]

    return schemas.live_chat.LeadList(items=leads, pagination=pagination)
