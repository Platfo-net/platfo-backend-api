from pydantic import UUID4

from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session


router = APIRouter(prefix="/group")


@router.get("/{facebook_page_id}", response_model=schemas.postman.GroupListApi)
def get_groups(
    *,
    db: Session = Depends(deps.get_db),
    facebook_page_id: str,
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
        user_id=current_user.id
    )

    groups = []

    for item in items:
        sample_contacts = services.postman.group_contact.get_by_group_and_count(
            db, group_id=item.id, count=4)

        sample_contacts_id = [contact.id for contact in sample_contacts]

        group_sample_contacts = services.live_chat.contact.get_bulk(
            db, contacts_id=sample_contacts_id)
        samples = []
        for sample in group_sample_contacts:
            samples.append(
                schemas.postman.ContactSample(
                    profile_image=sample.information.get('profile_image', None),
                    username=sample.information.get('username', None),
                )
            )
        groups.append(
            schemas.postman.Group(
                id=item.id,
                name=item.name,
                description=item.description,
                contacts=samples
            )
        )

    return schemas.postman.GroupListApi(
        pagination=pagination,
        items=groups
    )


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
    db_obj = services.postman.group.create(
        db,
        obj_in=schemas.postman.GroupCreate(
            name=obj_in.name,
            description=obj_in.description,
            facebook_page_id=obj_in.facebook_page_id
        ),
        user_id=current_user.id,
    )

    services.postman.group_contact.create_bulk(
        db, objs_in=obj_in.contacts, group_id=db_obj.id)

    return schemas.postman.Group(
        id=db_obj.id,
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
    services.postman.group_contact.remove_bulk(db, group_id=id)
    services.postman.group.remove(db, id=id, user_id=current_user.id)

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

    db_obj = services.postman.group.get(db, id=id)
    group = services.postman.group.update(
        db,
        db_obj=db_obj,
        user_id=current_user.id,
        obj_in=schemas.postman.GroupUpdate(
            name=obj_in.name,
            description=obj_in.description
        ),
    )
    services.postman.group_contact.remove_bulk(db, group_id=id)

    services.postman.group_contact.create_bulk(
        db, objs_in=obj_in.contacts, group_id=db_obj.id)

    return schemas.postman.Group(name=group.name, description=group.description)
