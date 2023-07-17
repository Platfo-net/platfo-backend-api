from datetime import date
from typing import List

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
        user_page_id=contact.user_page_id,
        user_id=contact.user_id,
        id=contact.uuid,
        last_message_at=contact.last_message_at,
        information=contact.information,
        last_message=str(contact.last_message),
        live_comment_count=contact.live_comment_count,
        comment_count=contact.comment_count,
        message_count=contact.message_count,
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


@router.post('/all/{facebook_page_id}')
def get_all_contact_based_on_filters(
    *,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(deps.get_db),
    facebook_page_id: int,
    from_datetime: date,    
    is_user_follow_buisiness: bool,
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
        obj_in=obj_in,
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
            user_page_id=contact.user_page_id,
            id=contact.uuid,
            last_message_at=contact.last_message_at,
            information=contact.information,
            last_message=contact.last_message,
            user_id=contact.user_id,
            live_comment_count=contact.live_comment_count,
            comment_count=contact.comment_count,
            message_count=contact.message_count,
            first_impression=contact.first_impression,
        )
        for contact in contacts
    ]

    return schemas.live_chat.ContactList(items=contacts, pagination=pagination)
