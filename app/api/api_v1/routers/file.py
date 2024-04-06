import uuid

from fastapi import APIRouter, File, Security, UploadFile

from app import models, schemas
from app.api import deps
from app.constants.role import Role
from app.core import storage
from app.core.config import settings

router = APIRouter(prefix="/file", tags=["File"])


@router.post("/upload/user/profile", response_model=schemas.Image)
async def upload_user_profile_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    filename = f"{uuid.uuid4()}-{file.filename}"
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_USER_PROFILE_BUCKET
    )

    return storage.get_image(uploaded_file_name, settings.S3_CAMPAIGN_BUCKET)


@router.post("/upload/shop/product", response_model=schemas.Image)
async def upload_shop_product_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    filename = f"{uuid.uuid4()}-{file.filename}"
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_SHOP_PRODUCT_IMAGE_BUCKET
    )

    return storage.get_image(uploaded_file_name, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)


@router.post("/upload/shop/category", response_model=schemas.Image)
async def upload_shop_category_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    filename = f"{uuid.uuid4()}-{file.filename}"
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_SHOP_CATEGORY_IMAGE_BUCKET
    )

    return storage.get_image(uploaded_file_name, settings.S3_SHOP_CATEGORY_IMAGE_BUCKET)


@router.post("/upload/shop/order/payment-receipt", response_model=schemas.Image)
async def upload_payment_receipt_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    filename = f"{uuid.uuid4()}-{file.filename}"
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_PAYMENT_RECEIPT_IMAGE
    )

    return storage.get_image(uploaded_file_name, settings.S3_PAYMENT_RECEIPT_IMAGE)


@router.post("/upload/telegram/menu-image", response_model=schemas.Image)
async def upload_telegram_menu_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    filename = f"{uuid.uuid4()}-{file.filename}"
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_TELEGRAM_BOT_MENU_IMAGES_BUCKET

    )

    return storage.get_image(uploaded_file_name, settings.S3_TELEGRAM_BOT_MENU_IMAGES_BUCKET)
