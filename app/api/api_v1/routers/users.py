from typing import Any, List
from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from app.constants.errors import Error
from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

from app.core.exception import raise_http_exception

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserRegister,
) -> Any:
    """
    register user
    """

    user = services.user.get_by_email(db, email=user_in.email)

    if user and user.is_active:
        raise_http_exception(Error.USER_EXIST_ERROR)
    if not user.is_active:
        raise_http_exception(Error.INACTIVE_USER)

    services.user.register(db, obj_in=user_in)
    return


@router.get("/all", response_model=List[schemas.User])
def get_users(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
) -> Any:
    """
    register user
    """

    users = services.user.get_multi(db, skip=0, limit=20)
    new_users = []
    for user in users:
        user.id = user.uuid
        user.role.id = user.role.uuid
        new_users.append(user)
    return new_users


def update_user_me(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserUpdate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
) -> Any:
    user = services.user.get(db, id=current_user.id)
    user = services.user.update(db, db_obj=user, obj_in=user_in)

    return user


@router.put("/", response_model=schemas.User)
def change_password_me(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserUpdatePassword,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
) -> Any:
    user = services.user.get(db, id=current_user.id)
    user = services.user.change_password(db, user_id=user.id, obj_in=user_in)

    return user


@router.get("/me", response_model=schemas.User)
def get_user_me(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
                Role.USER["name"],
            ],
        ),
) -> Any:
    user = services.user.get(db, id=current_user.id)
    user.id = user.uuid
    user.role.id = user.role.uuid
    return user
