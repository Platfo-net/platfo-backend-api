from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/group')


@router.get('/{facebook_page_id}', response_model=schemas.notifier.GroupListApi)
def get_groups(
    *,
    db: Session = Depends(deps.get_db),
    facebook_page_id: int,
    page: int = 1,
    page_size: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    pagination, items = services.notifier.group.get_multi(
        db,
        facebook_page_id=facebook_page_id,
        page=page,
        page_size=page_size,
        user_id=current_user.id,
    )
    groups = []
    for item in items:
        groups.append(
            schemas.notifier.Group(
                id=item.uuid, name=item.name, description=item.description
            )
        )
    return schemas.notifier.GroupListApi(pagination=pagination, items=groups)


@router.post('/', response_model=schemas.notifier.Group)
def create_group(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.notifier.GroupCreateApiSchemas,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    if not obj_in.contacts:
        raise_http_exception(Error.GROUP_EMPTY_CONTACT)
    contacts = services.live_chat.contact.get_bulk_by_uuid(
        db, contacts_id=obj_in.contacts
    )
    for contact in contacts:
        if contact.facebook_page_id != obj_in.facebook_page_id:
            raise_http_exception(Error.CONTACTS_DO_NOT_BELONGS_TO_THIS_PAGE)

    group = services.notifier.group.create(
        db,
        obj_in=schemas.notifier.GroupCreate(
            name=obj_in.name,
            description=obj_in.description,
            facebook_page_id=obj_in.facebook_page_id,
        ),
        user_id=current_user.id,
    )

    contacts_in = [
        schemas.notifier.GroupContactCreate(
            contact_id=item.id,
            contact_igs_id=item.contact_igs_id,
        )
        for item in contacts
    ]
    services.notifier.group_contact.create_bulk(
        db, objs_in=contacts_in, group_id=group.id
    )

    return schemas.notifier.Group(
        id=group.uuid, name=group.name, description=group.description
    )


@router.delete('/{id}')
def remove_group(
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
    group = services.notifier.group.get_by_uuid(db, uuid=id)
    if not group:
        raise_http_exception(Error.GROUP_NOT_FOUND)
    if group.user_id != current_user.id:
        raise_http_exception(Error.GROUP_NOT_FOUND_ACCESS_DENIED)

    services.notifier.group_contact.remove_bulk(db, group_id=group.id)
    services.notifier.group.remove(db, id=group.id)

    return


@router.put('/{id}', response_model=schemas.notifier.Group)
def update_group(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    obj_in: schemas.notifier.GroupUpdateApiSchemas,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    db_obj = services.notifier.group.get_by_uuid(db, uuid=id)
    if not db_obj:
        raise_http_exception(Error.GROUP_NOT_FOUND)

    if db_obj.user_id != current_user.id:
        raise_http_exception(Error.GROUP_NOT_FOUND)

    for contact in obj_in.contacts:
        if contact.facebook_page_id != obj_in.facebook_page_id:
            raise_http_exception(Error.CONTACTS_DO_NOT_BELONGS_TO_THIS_PAGE)

    group = services.notifier.group.update(
        db,
        db_obj=db_obj,
        obj_in=schemas.notifier.GroupUpdate(
            name=obj_in.name, description=obj_in.description
        ),
    )
    services.notifier.group_contact.remove_by_group_id(db, group_id=group.id)

    contacts = services.live_chat.contact.get_bulk_by_uuid(
        db, contacts_id=obj_in.contacts
    )

    contacts_in = [
        schemas.notifier.GroupContactCreate(
            contact_id=contact.id,
            contact_igs_id=contact.contact_igs_id,
        )
        for contact in contacts
    ]
    services.notifier.group_contact.create_bulk(
        db, objs_in=contacts_in, group_id=db_obj.id
    )

    return schemas.notifier.Group(
        id=group.uuid, name=group.name, description=group.description
    )
