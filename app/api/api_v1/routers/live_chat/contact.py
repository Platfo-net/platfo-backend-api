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

    contact = services.live_chat.contact.get(db, id=id)

    if not contact:
        raise HTTPException(
            status_code=Error.CONTACT_NOT_FOUND["status_code"],
            detail=Error.CONTACT_NOT_FOUND["text"],
        )

    return schemas.live_chat.Contact(
        contact_igs_id=contact.contact_igs_id,
        user_page_id=contact.user_page_id,
        user_id=contact.user_id,
        id=contact.id,
        last_message_at=contact.last_message_at,
        information=contact.information,
        last_message=contact.last_message,
        live_comment_count=contact.live_comment_count,
        comment_count=contact.comment_count,
        message_count=contact.message_count
    )


@router.get("/page/{page_id}", response_model=List[schemas.live_chat.Contact])
def get_pages_contacts(
    *,
    db: Session = Depends(deps.get_db),
    page_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    contacts = services.live_chat.contact.get_pages_contacts(
        db, page_id=page_id, skip=skip, limit=limit
    )

    return [
        schemas.live_chat.Contact(
            contact_igs_id=contact.contact_igs_id,
            user_page_id=contact.user_page_id,
            id=contact.id,
            last_message_at=contact.last_message_at,
            information=contact.information,
            last_message=contact.last_message,
            user_id=contact.user_id,
            live_comment_count=contact.live_comment_count,
            comment_count=contact.comment_count,
            message_count=contact.message_count
        )
        for contact in contacts
        if len(contacts)
    ]


@router.put("/{page_id}")
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


@router.post("/search/all")
def get_all_contact_based_on_filters(
    *,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(deps.get_db),
    obj_in: List[schemas.live_chat.SearchItem],
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    valid_fields = ["message_count", "comment_count", "live_comment_count"]
    valid_operators = ["lte", "lt", "gt", "gte", "ne", "eq"]

    for obj in obj_in:
        if obj.field not in valid_fields or obj.operator not in valid_operators:
            raise HTTPException(
                status_code=Error.INVALID_FIELDS_OPERATORS["status_code"],
                detail=Error.INVALID_FIELDS_OPERATORS["text"],
            )
    contacts, pagination = services.live_chat.contact. \
        search(db=db, obj_in=obj_in, page=page, page_size=page_size)

    contacts = [schemas.live_chat.Contact(
        contact_igs_id=contact.contact_igs_id,
        user_page_id=contact.user_page_id,
        id=contact.id,
        last_message_at=contact.last_message_at,
        information=contact.information,
        last_message=contact.last_message,
        user_id=contact.user_id,
        live_comment_count=contact.live_comment_count,
        comment_count=contact.comment_count,
        message_count=contact.message_count
    ) for contact in contacts if len(contacts)]

    return schemas.live_chat.ContactList(contacts=contacts, pagination=pagination)
