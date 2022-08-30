
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
    return content


@router.put('/')
def update_content():
    pass


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



