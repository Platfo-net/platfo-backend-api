from app.constants.errors import Error
from pydantic import UUID4

from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session


router = APIRouter(prefix="/group")


@router.get("/{facebook_page_id}", response_model=schemas.postman.GroupListApi)
def get_groups(
    *,
    db: Session = Depends(deps.get_db),
    facebook_page_id: int,
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

    pagination, items = services.postman.group.get_multi(
        db,
        facebook_page_id=facebook_page_id,
        page=page,
        page_size=page_size,
        user_id=current_user.id,
    )

    groups = []

    for item in items:
        sample_group_contacts = services.postman.group_contact.get_by_group_and_count(
            db, group_id=item.id, count=4
        )

        sample_contacts_id = [
            group_contact.contact_id for group_contact in sample_group_contacts
        ]

        group_sample_contacts = services.live_chat.contact.get_bulk(
            db, contacts_id=sample_contacts_id
        )
        samples = []
        for sample in group_sample_contacts:
            samples.append(
                schemas.postman.ContactSample(
                    profile_image=sample.information.get("profile_image", None),
                    username=sample.information.get("username", None),
                )
            )
        groups.append(
            schemas.postman.GroupContactSample(
                id=item.uuid,
                name=item.name,
                description=item.description,
                contacts=samples,
            )
        )

    return schemas.postman.GroupListApi(pagination=pagination, items=groups)


@router.post("/", response_model=schemas.postman.Group)
def create_group(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.postman.GroupCreateApiSchemas,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    if not obj_in.contacts:
        raise HTTPException(
            status_code=Error.GROUP_EMPTY_CONTACT["status_code"],
            detail=Error.GROUP_EMPTY_CONTACT["text"],
        )

    db_obj = services.postman.group.create(
        db,
        obj_in=schemas.postman.GroupCreate(
            name=obj_in.name,
            description=obj_in.description,
            facebook_page_id=obj_in.facebook_page_id,
        ),
        user_id=current_user.id,
    )

    contacts_uuid = [item.contact_id for item in obj_in.contacts]
    contacts = services.live_chat.contact.get_bulk_by_uuid(db, contacts_id=contacts_uuid)

    contacts_in = [
        schemas.postman.GroupContactCreate(
            contact_id=item.id,
            contact_igs_id=item.contact_igs_id,
        )for item in contacts
    ]
    services.postman.group_contact.create_bulk(
        db, objs_in=contacts_in, group_id=db_obj.id
    )

    return schemas.postman.Group(
        id=db_obj.uuid,
        name=db_obj.name,
        description=db_obj.description
    )


@router.delete("/{id}")
def remove_group(
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
    group = services.postman.group.get_by_uuid(db, id)
    if not group:
        raise HTTPException(
            status_code=Error.GROUP_NOT_FOUND["status_code"],
            detail=Error.GROUP_NOT_FOUND["text"],
        )
    if group.user_id != current_user.id:
        raise HTTPException(
            status_code=Error.GROUP_NOT_FOUND_ACCESS_DENIED["status_code"],
            detail=Error.GROUP_NOT_FOUND_ACCESS_DENIED["text"],
        )

    services.postman.group_contact.remove_bulk(db, group_id=group.id)
    services.postman.group.remove(db, id=group.id)

    return


@router.put("/{id}", response_model=schemas.postman.Group)
def update_group(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    obj_in: schemas.postman.GroupUpdateApiSchemas,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
):
    if not obj_in.contacts:
        raise HTTPException(
            status_code=Error.GROUP_EMPTY_CONTACT["status_code"],
            detail=Error.GROUP_EMPTY_CONTACT["text"],
        )

    db_obj = services.postman.group.get_by_uuid(db, id)

    group = services.postman.group.update(
        db,
        db_obj=db_obj,
        user_id=current_user.id,
        obj_in=schemas.postman.GroupUpdate(
            name=obj_in.name, description=obj_in.description
        ),
    )
    services.postman.group_contact.remove_bulk(db, group_id=group.id)

    contacts_uuid = [item.contact_id for item in obj_in.contacts]
    contacts = services.live_chat.contact.get_bulk_by_uuid(db, contacts_id=contacts_uuid)

    contacts_in = [
        schemas.postman.GroupContactCreate(
            contact_id=item.id,
            contact_igs_id=item.contact_igs_id,
        )for item in contacts
    ]
    services.postman.group_contact.create_bulk(
        db, objs_in=contacts_in, group_id=db_obj.id
    )

    return schemas.postman.Group(
        id=group.uuid, name=group.name, description=group.description
    )
