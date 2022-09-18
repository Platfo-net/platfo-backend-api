from typing import Any, List
from app import services, models, schemas
from app.api import deps
from app.constants.role import Role
from app.constants.errors import Error
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from pydantic.types import UUID4
from app.core.cache import get_password_data
from redis.client import Redis

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
    if user:
        raise HTTPException(
            status_code=Error.USER_EXIST_ERROR["status_code"],
            detail=Error.USER_EXIST_ERROR["text"],
        )
    user = services.user.register(db, obj_in=user_in)
    return


@router.post("", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    user = services.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=Error.USER_EXIST_ERROR["status_code"],
            detail=Error.USER_EXIST_ERROR["text"],
        )
    user = services.user.create(db, obj_in=user_in)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
        ],
    ),
) -> Any:
    user = services.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=Error.NO_USER_WITH_THE_GIVEN_ID['status_code'],
            detail=Error.NO_USER_WITH_THE_GIVEN_ID['text'],
        )

    services.user.remove(db, id=user_id)
    return


@router.get("/all", response_model=List[schemas.User])
def get_all_users(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
        ],
    ),
) -> Any:

    return services.user.get_multi(db, skip=skip, limit=limit)


@router.put("/me",  response_model=schemas.User)
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


@router.put("/",  response_model=schemas.User)
def change_password_me(
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
    user = services.user.get(db , id = current_user.id)
    return user


@router.post("/forget-password", status_code=status.HTTP_200_OK)
async def forget_password(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.ForgetPassword,
):
    user = services.user.get_by_email(db, email=user_in.email)
    if user is None:
        raise HTTPException(
            status_code=Error.USER_NOT_FOUND['status_code'],
            detail=Error.USER_NOT_FOUND['text'],
        )
    await services.user.send_recovery_mail(db, user.email)


@router.post("/recovery-password", status_code=status.HTTP_200_OK)
def recovery_password(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.ChangePassword,
    redis_client: Redis = Depends(deps.get_redis_client)
):

    code = get_password_data(client=redis_client, code=user_in.code)
    if code is None:
        raise HTTPException(
            status_code=Error.CODE_EXPIRATION_OR_NOT_EXIST_ERROR
            ["status_code"],
            detail=Error.CODE_EXPIRATION_OR_NOT_EXIST_ERROR
            ["text"],
        )
    if str(code.decode('utf-8')) != str(user_in.code):
        raise HTTPException(
            status_code=Error.CODE_EXPIRATION_OR_NOT_EXIST_ERROR
            ["status_code"],
            detail=Error.CODE_EXPIRATION_OR_NOT_EXIST_ERROR
            ["text"],
        )
    user = services.user.get_by_email(db, email=user_in.email)
    services.user.change_password(
        db, user_id=user.id, new_password=user_in.new_password)
    return
