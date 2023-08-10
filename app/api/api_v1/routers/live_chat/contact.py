from datetime import date

from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/contact')


@router.get('/{id}', response_model=schemas.live_chat.Contact)
def get_contact(
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
        Api for getting and specific contact data

    Args:

        id (UUID4): id of contact in system:
                eg: 3c8f64ca-f1b0-4692-9833-232c4b560d2f

    Raises:

        HTTPException 404: when contact not found

    """

    contact = services.live_chat.contact.get_by_uuid(db, id)

    if not contact:
        raise_http_exception(Error.CONTACT_NOT_FOUND)

    return schemas.live_chat.Contact(
        contact_igs_id=contact.contact_igs_id,
        facebook_page_id=contact.facebook_page_id,
        user_id=contact.user_id,
        id=contact.uuid,
        last_message_at=contact.last_message_at,
        last_interaction_at=contact.last_interaction_at,
        last_message=contact.last_message,
        username=contact.username,
        profile_image=contact.profile_image,
        name=contact.name,
        followers_count=contact.followers_count,
        is_verified_user=contact.is_verified_user,
        is_user_follow_business=contact.is_user_follow_business,
        is_business_follow_user=contact.is_business_follow_user,

    )


@router.put('/{page_id}', deprecated=True)
def update_page_contacts_information(
    *,
    db: Session = Depends(deps.get_db),
    contact_igs_id: str,
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
    contacts = services.live_chat.contact.update_information(
        db, contact_igs_id=contact_igs_id, data=data
    )

    return contacts


@router.post('/all/{facebook_page_id}', response_model=schemas.live_chat.ContactList)
def get_all_contact_based_on_filters(
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

    contacts, pagination = services.live_chat.contact.get_multi(
        db=db,
        facebook_page_id=facebook_page_id,
        is_user_follow_business=is_user_follow_business,
        from_date=from_date,
        page=page,
        page_size=page_size,
    )

    if not contacts:
        return schemas.live_chat.ContactList(
            items=[],
            pagination=schemas.Pagination(),
        )

    contacts = [
        schemas.live_chat.Contact(
            contact_igs_id=contact.contact_igs_id,
            facebook_page_id=contact.facebook_page_id,
            id=contact.uuid,
            last_message_at=contact.last_message_at,
            last_interaction_at=contact.last_interaction_at,
            last_message=contact.last_message,
            first_impression=contact.first_impression,
            profile_image=contact.profile_image,
            username=contact.username,
            name=contact.name,
            followers_count=contact.followers_count,
            is_verified_user=contact.is_verified_user,
            is_user_follow_business=contact.is_user_follow_business,
            is_business_follow_user=contact.is_business_follow_user,

        )
        for contact in contacts
    ]

    return schemas.live_chat.ContactList(items=contacts, pagination=pagination)
