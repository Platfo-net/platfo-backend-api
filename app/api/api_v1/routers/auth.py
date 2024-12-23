# from logging import Logger
from typing import Any

from fastapi import APIRouter, Body, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
# from opentelemetry.semconv.trace import HttpFlavorValues, SpanAttributes
# from opentelemetry.trace import SpanKind, Tracer
from redis.client import Redis
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.core import cache, security, storage, tasks, utils
from app.core.config import settings
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/access-token', response_model=schemas.Token)
def login_access_token_by_email(
    *,
    db: Session = Depends(deps.get_db),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    data: schemas.LoginFormByEmail,
):

    # with tracer.start_as_current_span(
    # "login_access_token_by_email", kind=SpanKind.SERVER) as span:
    #     span.set_attributes(
    #         {
    #             SpanAttributes.HTTP_METHOD: "POST",
    #             SpanAttributes.HTTP_FLAVOR: str(HttpFlavorValues.HTTP_1_1),
    #             SpanAttributes.HTTP_URL: "access-token",
    #         }
    #     )
    # logger.info(
    #     "login_access_token_by_email",
    #     extra={"tags": {"email": data.email}},
    # )
    user = services.user.authenticate_by_email(
        db, email=data.email, password=data.password
    )

    if not user:
        raise_http_exception(Error.USER_PASS_WRONG_ERROR)
    if not user.is_email_verified:
        raise_http_exception(Error.EMAIL_NOT_VERIFIED)
    elif not user.is_active:
        raise_http_exception(Error.INACTIVE_USER)

    return security.create_token(db, user=user)


@router.post('/access-token-phone-number', response_model=schemas.Token)
def login_access_token_by_phone_number(
    *,
    db: Session = Depends(deps.get_db),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    data: schemas.LoginFormByPhoneNumber,
) -> Any:
    user = services.user.authenticate_by_phone_number(
        db,
        phone_number=data.phone_number,
        phone_country_code=data.phone_country_code,
        password=data.password,
    )

    if not user:
        raise_http_exception(Error.USER_PASS_WRONG_ERROR)
    elif not user.is_active:
        raise_http_exception(Error.INACTIVE_USER)

    return security.create_token(db, user=user)


@router.post('/token-swagger', response_model=schemas.Token)
def login_access_token_swagger(
    db: Session = Depends(deps.get_db),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = services.user.authenticate_by_email(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise_http_exception(Error.USER_PASS_WRONG_ERROR)
    elif not user.is_active:
        raise_http_exception(Error.INACTIVE_USER)

    return security.create_token(db, user=user)


@router.post('/check', response_model=schemas.User)
def test_token(
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Test access token
    """

    role = services.role.get(db, current_user.role_id)

    return schemas.User(
        id=current_user.uuid,
        email=current_user.email,
        is_active=current_user.is_active,
        phone_number=current_user.phone_number,
        phone_country_code=current_user.phone_country_code,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        role=schemas.Role(
            name=role.name,
            description=role.description,
            id=role.uuid,
            persian_name=role.persian_name,
        ),
        profile_image=storage.get_image(
            current_user.profile_image, settings.S3_USER_PROFILE_BUCKET
        ),
    )


@router.post('/hash-password', response_model=str)
def hash_password(
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    password: str = Body(..., embed=True),
) -> Any:
    """
    Hash a password
    """
    return security.get_password_hash(password)


@router.post('/forgot-password', response_model=schemas.RegisterCode)
def forgot_password(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client_for_reset_password),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    obj_in: schemas.PhoneData,
):
    user = services.user.get_by_phone_number(
        db, phone_number=obj_in.phone_number, phone_country_code=obj_in.phone_country_code)
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    data = cache.get_user_reset_password_code(
        redis_client, user.phone_number, user.phone_country_code)

    if data:
        raise_http_exception(Error.RESET_PASSWORD_CODE_HAVE_BEEN_ALREADY_SENT)

    token = utils.generate_random_token(64)
    code = utils.generate_random_code(4)
    result = cache.set_user_reset_password_code(
        redis_client,
        user.phone_number, user.phone_country_code,
        code, token
    )

    if not result:
        raise_http_exception(Error.UNEXPECTED_ERROR)

    tasks.send_user_reset_password_code.delay(
        f'+{user.phone_country_code}{user.phone_number}', code
    )
    return schemas.RegisterCode(token=token)


@router.post('/change-password', status_code=status.HTTP_200_OK)
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client_for_reset_password),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    obj_in: schemas.ChangePassword,
):
    user = services.user.get_by_phone_number(
        db, phone_number=obj_in.phone_number, phone_country_code=obj_in.phone_country_code)
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    data = cache.get_user_reset_password_code(
        redis_client, obj_in.phone_number, obj_in.phone_country_code)
    if not data:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    code = data.get('code', None)
    token = data.get('token', None)
    if not (token and code):
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    if not token == obj_in.token:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)
    if not code == obj_in.code:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)
    services.user.change_password(db, db_user=user, password=obj_in.password)
    cache.remove_data_from_cache(redis_client, f'{obj_in.phone_country_code}{obj_in.phone_number}')
    return


@router.post('/send-activation-code-by-sms', response_model=schemas.RegisterCode)
def send_activation_code_by_sms(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client_for_user_activation),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    phone_data: schemas.PhoneData,
):
    user = services.user.get_by_phone_number(
        db,
        phone_number=phone_data.phone_number,
        phone_country_code=phone_data.phone_country_code,
    )
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    if user.is_active:
        raise_http_exception(Error.USER_IS_ACTIVE)

    data = cache.get_user_registeration_activation_code(
        redis_client, user.phone_number, user.phone_country_code
    )

    if data:
        raise_http_exception(Error.ACTIVATION_CODE_HAVE_BEEN_ALREADY_SENT)

    token = utils.generate_random_token(64)

    code = utils.generate_random_code(5)

    result = cache.set_user_registeration_activation_code(
        redis_client, user.phone_number, user.phone_country_code, code, token
    )

    if not result:
        raise_http_exception(Error.UNEXPECTED_ERROR)

    tasks.send_user_activation_code.delay(
        f'+{user.phone_country_code}{user.phone_number}', code
    )

    return schemas.RegisterCode(token=token)


@router.post('/activate-by-sms', status_code=status.HTTP_200_OK)
def activate_user_by_sms(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client_for_user_activation),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    activation_data: schemas.ActivationDataByPhoneNumber,
):
    user = services.user.get_by_phone_number(
        db,
        phone_number=activation_data.phone_number,
        phone_country_code=activation_data.phone_country_code,
    )
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    data = cache.get_user_registeration_activation_code(
        redis_client, user.phone_number, user.phone_country_code
    )
    if not data:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    code = data.get('code', None)
    token = data.get('token', None)

    if not (token and code):
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    if not token == activation_data.token:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    if not code == activation_data.code:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    services.user.activate(db, user=user)

    cache.remove_data_from_cache(
        redis_client,
        '{}{}'.format(
            user.phone_number,
            user.phone_country_code,
        ),
    )

    return


@router.post(
    '/send-activation-code-by-email',
    response_model=schemas.RegisterCode,
    deprecated=True,
)
def send_activation_email(
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client_for_user_activation),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    email: str = Body(..., embed=True),
):
    return
    user = services.user.get_by_email(db, email=email)
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    if user.is_active:
        raise_http_exception(Error.USER_IS_ACTIVE)

    data = cache.get_user_registeration_activation_code_by_email(redis_client, email)

    if data:
        raise_http_exception(Error.ACTIVATION_CODE_HAVE_BEEN_ALREADY_SENT)

    token = utils.generate_random_token(64)
    code = utils.generate_random_code(6)
    result = cache.set_user_registeration_activation_code_by_email(
        redis_client, email, code, token
    )
    if not result:
        raise_http_exception(Error.UNEXPECTED_ERROR)
    # TODO Send activation email
    return schemas.RegisterCode(token=token)


@router.post('/activate-by-email', status_code=status.HTTP_200_OK, deprecated=True)
def activate_user_by_email(
    *,
    db: Session = Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client_for_user_activation),
    # logger: Logger = Depends(deps.logger_factory(router)),
    # tracer: Tracer = Depends(deps.tracer_factory(router)),
    activation_data: schemas.ActivationDataByEmail,
):
    return
    user = services.user.get_by_email(db, email=activation_data.email)
    if not user:
        raise_http_exception(Error.USER_NOT_FOUND)

    data = cache.get_user_registeration_activation_code_by_email(
        redis_client, email=activation_data.email
    )
    if not data:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    code = data.get('code', None)
    token = data.get('token', None)
    if not (token and code):
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    if not token == activation_data.token:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    if not code == activation_data.code:
        raise_http_exception(Error.INVALID_CODE_OR_TOKEN)

    services.user.activate(db, user=user)
    services.user.verify_email(db, user=user)
    cache.remove_data_from_cache(redis_client, key=activation_data.email)

    return
