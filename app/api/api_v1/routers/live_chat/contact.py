from typing import List

from pydantic import UUID4

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

router = APIRouter(prefix="/contact")


@router.get("/{id}", response_model=schemas.live_chat.Contact)
def get_contact(
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
        raise HTTPException(
            status_code=Error.CONTACT_NOT_FOUND["status_code"],
            detail=Error.CONTACT_NOT_FOUND["text"],
        )

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


@router.put("/{page_id}" , deprecated=True)
def update_page_contacts_information(
        *,
        db: Session = Depends(deps.get_db),
        contact_igs_id: str,
        obj_in: schemas.live_chat.ProfileUpdate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    data = dict()
    data[obj_in.key] = obj_in.value
    contacts = services.live_chat.contact.update_information(
        db, contact_igs_id=contact_igs_id, data=data
    )

    return contacts


@router.post("/all/{facebook_page_id}")
def get_all_contact_based_on_filters(
        *,
        page: int = 1,
        page_size: int = 20,
        db: Session = Depends(deps.get_db),
        facebook_page_id: int,
        obj_in: List[schemas.live_chat.SearchItem],
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    """
    Searching in contacts based on filters
    Args:
        Valid Operators:
            LTE: Less than or equal to

            GTE: Greater than or equal to

            LT: Less than

            GT: Greater than

            NE: Not equal to

            EQ: Equal to


        Valid Field Name:

            message_count

            comment_count

            live_comment_count
    """
    account = services.instagram_page.get_by_facebook_page_id(db , facebook_page_id=facebook_page_id)
    if account.user_id != current_user.id :
        raise HTTPException(
            status_code=Error.ACCOUNT_NOT_FOUND["status_code"],
            detail=Error.ACCOUNT_NOT_FOUND["text"],
        )
    if not account:
        raise HTTPException(
            status_code=Error.ACCOUNT_NOT_FOUND["status_code"],
            detail=Error.ACCOUNT_NOT_FOUND["text"],
        )
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
