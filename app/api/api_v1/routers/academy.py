
from typing import List

from fastapi import APIRouter, Depends,\
    Security, HTTPException, Query
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role

router = APIRouter(prefix="/academy", tags=["Academy"])


@router.get("/label/all", response_model=schemas.academy.LabelListApi)
def get_labels_list(
        *,
        db: Session = Depends(deps.get_db),
        page: int = 1,
        page_size: int = 20
):
    labels, pagination = services.academy.label.get_multi(
        db,
        page=page,
        page_size=page_size,
    )

    return schemas.academy.LabelListApi(
        labels=labels,
        pagination=pagination
    )


@router.post('/label/create', response_model=schemas.academy.Label)
def create_label(
        *,
        obj_in: schemas.academy.LabelCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    label = services.academy.label.create(obj_in=obj_in, db=db)
    return label


@router.put('/label/update/{id}', response_model=schemas.academy.Label)
def update_label(
        *,
        obj_in: schemas.academy.LabelUpdate,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    label = services.academy.label.get(db, id)
    if not label:
        raise HTTPException(
            status_code=Error.CATEGORY_NOT_FOUND['status_code'],
            detail=Error.CATEGORY_NOT_FOUND['text']
        )
    label = services.academy.label.update(
        db, db_obj=label, obj_in=obj_in)

    return label


@router.delete('/label/delete/{id}')
def delete_label(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
           deps.get_current_active_user,
           scopes=[
               Role.ADMIN["name"],
           ],
        ),
):
    label = services.academy.label.get(db, id=id)
    if not label:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text']
        )
    services.academy.label.remove(db, id=id)
    return


@router.get("/category/all", response_model=schemas.academy.CategoryListApi)
def get_categories_list(
        *,
        db: Session = Depends(deps.get_db),
        page: int = 1,
        page_size: int = 20
):
    categories, pagination = services.academy.category.get_multi(
        db,
        page=page,
        page_size=page_size,
    )

    def categories_to_child_categories(n=None):
        categories_list = [{
            "id": category.id,
            "title": category.title,
            "children": categories_to_child_categories(category.id),
            "parent_id": category.parent_id
        }
            for category in categories if category.parent_id == n
        ]
        return categories_list

    categories_tree = schemas.academy.CategoryListApi(
        categories=categories_to_child_categories(),
        pagination=pagination
    )
    return categories_tree


@router.post('/category/create', response_model=schemas.academy.Category)
def create_category(
        *,
        obj_in: schemas.academy.CategoryCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    category = services.academy.category.create(obj_in=obj_in, db=db)
    return category


@router.put('/category/update/{id}', response_model=schemas.academy.Category)
def update_category(
        *,
        obj_in: schemas.academy.CategoryUpdate,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    category = services.academy.category.get(db, id)
    if not category:
        raise HTTPException(
            status_code=Error.CATEGORY_NOT_FOUND['status_code'],
            detail=Error.CATEGORY_NOT_FOUND['text']
        )
    category = services.academy.category.update(
        db, db_obj=category, obj_in=obj_in)

    return category


@router.delete('/category/delete/{id}')
def delete_category(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
          deps.get_current_active_user,
          scopes=[
             Role.ADMIN["name"],
          ],
        ),
):
    category = services.academy.category.get(db, id=id)
    if not category:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text']
        )
    services.academy.category.remove(db, id=id)
    return


@router.get('/search', response_model=schemas.academy.ContentSearch)
def search_content_by_category(
        *,
        page: int = 1,
        page_size: int = 20,
        categories_list_id: List[UUID4] = Query(None),
        db: Session = Depends(deps.get_db)
):
    contents, pagination = services.academy.content.search(
        db,
        categories_list=categories_list_id,
        page=page,
        page_size=page_size
    )
    if not contents:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text']
        )

    for content in contents:
        return schemas.academy.ContentSearch(
            contents=content,
            pagination=pagination
        )


@router.get('/', response_model=schemas.academy.ContentListApi)
def get_all_contents(
         *,
         db: Session = Depends(deps.get_db),
         page: int = 1,
         page_size: int = 20
):
    contents, pagination = services.academy.content.get_multi(
        db,
        page=page,
        page_size=page_size,
    )

    content_list = schemas.academy.ContentListApi(
        contents=contents,
        pagination=pagination
    )
    return content_list


@router.get('/{id}', response_model=schemas.academy.ContentDetail)
def get_content_by_id(
          *,
          db: Session = Depends(deps.get_db),
          id: UUID4
):
    content, categories, labels = services.academy.content.\
        get_by_detail(db, id=id)

    if not content:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text']
        )

    content_detail = [schemas.academy.ContentDetailList(
        id=content.id,
        title=content.title,
        is_published=content.is_published,
        slug=content.slug,
        blocks=content.blocks,
        cover_image=content.cover_image,
        caption=content.caption,
        version=content.version,
        time=content.time,
        created_at=content.created_at,
        updated_at=content.updated_at,
        categories=categories,
        labels=labels,
        user_id=content.user_id,
    )]

    return schemas.academy.ContentDetail(
        content_detail=content_detail
    )


@router.post('/', response_model=schemas.academy.Content)
def create_content(
        *,
        obj_in: schemas.academy.ContentCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
           deps.get_current_active_user,
           scopes=[
               Role.ADMIN["name"],
               Role.WRITER["name"]
           ],
        ),
):
    content = services.academy.content.create(db=db,
                                              obj_in=obj_in,
                                              user_id=current_user.id)
    for category in obj_in.categories:
        services.academy.category_content.create(
            db,
            category_id=category.category_id,
            content_id=content.id
        )
    for label in obj_in.labels:
        services.academy.label_content.create(
            db,
            label_id=label.label_id,
            content_id=content.id
        )

    return content


@router.put('/{id}', response_model=schemas.academy.Content)
def update_content(
           *,
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
    old_content = services.academy.content.get(db, id=id)

    if not old_content:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text'])

    content = services.academy.content.update(
        db, db_obj=old_content, obj_in=obj_in, user_id=current_user.id)

    services.academy.category_content.remove_by_content_id(
        db,
        content_id=id,
    )
    for category in obj_in.categories:
        services.academy.category_content.create(
            db,
            content_id=old_content.id,
            category_id=category.category_id
        )

    services.academy.label_content.remove_by_content_id(
        db,
        content_id=id,
    )
    for label in obj_in.labels:
        services.academy.label_content.create(
            db,
            label_id=label.label_id,
            content_id=old_content.id
        )

    return content


@router.delete('/{id}')
def delete_content(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
           deps.get_current_active_user,
           scopes=[
               Role.ADMIN["name"],
           ],
        ),
):
    content = services.academy.content.get(db, id=id)
    if not content:
        raise HTTPException(
            status_code=Error.CONTENT_NOT_FOUND['status_code'],
            detail=Error.CONTENT_NOT_FOUND['text']
        )
    services.academy.content.remove(db, id=id)
    return
