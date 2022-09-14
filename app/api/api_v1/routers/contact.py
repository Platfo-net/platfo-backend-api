

from typing import List

from pydantic import UUID4

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session


router = APIRouter(prefix="/contact", tags=["Contacts"])


@router.get("/{id}", response_model=schemas.Contact)
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

    contact = services.contact.get(db, id=id)

    if not contact:
        raise HTTPException(
            status_code=Error.CONTACT_NOT_FOUND['status_code'],
            detail=Error.CONTACT_NOT_FOUND['text']
        )

    return schemas.Contact(
        contact_igs_id=contact.contact_igs_id,
        user_page_id=contact.user_page_id,
        user_id=contact.user_id,
        id=contact.id,
        last_message_at=contact.last_message_at,
        information=contact.information,
        last_message=contact.last_message
    )


@router.get("/page/{page_id}",
            response_model=List[schemas.Contact]
            )
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
    contacts = services.contact.get_pages_contacts(
        db,
        page_id=page_id,
        skip=skip,
        limit=limit)

    return [
        schemas.Contact(
            contact_igs_id=contact.contact_igs_id,
            user_page_id=contact.user_page_id,
            id=contact.id,
            last_message_at=contact.last_message_at,
            information=contact.information,
            last_message=contact.last_message,
            user_id=contact.user_id
        ) for contact in contacts if len(contacts)
    ]


@router.put("/{page_id}")
def update_page_contacts_information(
    *,
    db: Session = Depends(deps.get_db),
    contact_igs_id: str,
    obj_in: schemas.ProfileUpdate,
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
    contacts = services.contact.update_information(
        db,
        contact_igs_id=contact_igs_id,
        data=data)

    return contacts
