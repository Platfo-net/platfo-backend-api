
from fastapi import APIRouter, Depends, Security, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role

router = APIRouter(prefix="/academy", tags=["Academy"])


@router.get("/category/all", response_model=schemas.academy.CategoryListApi)
def get_categories_list(
        *,
        db: Session = Depends(deps.get_db),
        page: int = 1,
        page_size: int = 20,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
):

    categories, pagination = services.category.get_multi(
             db,
             page=page,
             page_size=page_size,
        )
    category_list = schemas.academy.CategoryListApi(
        items=categories,
        pagination=pagination
    )
    return category_list


@router.post('/category/create', response_model=schemas.academy.Category)
def create_category(
        *, obj_in: schemas.academy.CategoryCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    category = services.category.create(obj_in=obj_in, db=db)
    return category


@router.put('/category/{id}', response_model=schemas.academy.Category)
def update_category(
        *, obj_in: schemas.academy.CategoryUpdate,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    category = services.category.get(db, id)
    if not category:
        raise HTTPException(
            status_code=Error.CATEGORY_NOT_FOUND['status_code'],
            detail=Error.CATEGORY_NOT_FOUND['text']
        )
    category = services.category.update(
        db, db_obj=category, obj_in=obj_in)

    return category


@router.delete('/category/{id}')
def delete_category(*,
           db: Session = Depends(deps.get_db),
           id: UUID4,
           current_user: models.User = Security(
               deps.get_current_active_user,
               scopes=[
                   Role.ADMIN["name"],
               ],
           ),
):
    category = services.category.get(db, id=id)
    if not category:
        raise HTTPException(
            status_code=Error.CATEGORY_NOT_FOUND['status_code'],
            detail=Error.CATEGORY_NOT_FOUND['text']
        )
    services.category.remove(db, id=id)
    return


@router.get('/', response_model=schemas.academy.ContentListApi)
def get_all_contents(*,
        db: Session = Depends(deps.get_db),
        page: int = 1,
        page_size: int = 20,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
):
    contents, pagination = services.content.get_multi(
        db,
        page=page,
        page_size=page_size,
    )
    content_list = schemas.academy.ContentListApi(
        items=contents,
        pagination=pagination
    )
    return content_list   


@router.get('/{id}', response_model=schemas.academy.ContentDetail)
def get_content_by_id(*,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
):
    content, categories = services.content.get_by_detail(db, id=id)

    if not content:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text']
        )
    content_attachments = services.content_attachment.\
        get_by_content_id(db, content_id=content.id)

    new_content_attachment = [
        schemas.academy.ContentAttachment(
            id=item.id,
            attachment_id=item.attachment_id
        )
        for item in content_attachments
    ]
    content_detail = [schemas.academy.ContentDetailList(
        id=content.id,
        title=content.title,
        detail=content.detail,
        categories=categories,
        content_attachments=new_content_attachment
    )]

    return schemas.academy.ContentDetail(
        content_detail=content_detail
    )


@router.post('/', response_model=schemas.academy.Content)
def create_content(*, obj_in: schemas.academy.ContentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    content = services.content.create(db=db, obj_in=obj_in)
    for category in obj_in.categories:
        services.category_content.create(
            db,
            category_id=category.category_id,
            content_id=content.id
        )
    for content_attachment in obj_in.content_attachments:
        services.content_attachment.create(
            db,
            obj_in=schemas.academy.ContentAttachmentCreate(
                attachment_id=content_attachment.attachment_id
            ),
            content_id=content.id
        )

    return content


@router.put('/{id}', response_model=schemas.academy.Content)
def update_content(*,
        db: Session = Depends(deps.get_db),
        id: str,
        obj_in: schemas.academy.ContentCreate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):

    old_content = services.content.get(db, id=id)

    if not old_content:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text'])

    content = services.content.update(
        db, db_obj=old_content, obj_in=obj_in)

    services.academy.content_attachment.remove_by_content_id(db, content_id=id)

    for content_attachment in obj_in.content_attachments:
        services.content_attachment.create(
            db,
            obj_in=schemas.academy.ContentAttachmentCreate(
                attachment_id=content_attachment.attachment_id
            ),
            content_id=old_content.id
        )
    services.academy.category_content.remove_by_content_id(
        db,
        content_id=id,
    )
    for category in obj_in.categories:
        services.category_content.create(
            db,
            content_id=old_content.id,
            category_id=category.category_id
        )

    return content


@router.delete('/{id}')
def delete_content(*,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    content = services.content.get(db, id=id)
    if not content:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text']
        )
    services.content.remove(db, id=id)
    return
