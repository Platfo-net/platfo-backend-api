import uuid

from fastapi import APIRouter, File, Security, UploadFile

from app import models, schemas
from app.api import deps
from app.constants.role import Role
from app.core import storage
from app.core.config import settings

router = APIRouter(prefix='/file', tags=['File'])


@router.post('/upload/notifier/campaign', response_model=schemas.Image)
async def upload_notifier_campaign_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    filename = f'{uuid.uuid4()}-{file.filename}'
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_CAMPAIGN_BUCKET
    )

    return storage.get_file(uploaded_file_name, settings.S3_CAMPAIGN_BUCKET)


@router.post('/upload/user/profile', response_model=schemas.Image)
async def upload_user_profile_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    filename = f'{uuid.uuid4()}-{file.filename}'
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_USER_PROFILE_BUCKET
    )

    return storage.get_file(uploaded_file_name, settings.S3_CAMPAIGN_BUCKET)


@router.post('/upload/shop/product', response_model=schemas.Image)
async def upload_shop_product_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    filename = f'{uuid.uuid4()}-{file.filename}'
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_SHOP_PRODUCT_IMAGE_BUCKET
    )

    return storage.get_file(uploaded_file_name, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)


@router.post('/upload/shop/order/payment-receipt', response_model=schemas.Image)
async def upload_payment_receipt_image(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.USER['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    filename = f'{uuid.uuid4()}-{file.filename}'
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.PAYMENT_RECEIPT_IMAGE
    )

    return storage.get_file(uploaded_file_name, settings.PAYMENT_RECEIPT_IMAGE)


# @router.get('/download', status_code=status.HTTP_200_OK)
# async def upload_payment_receipt_image(
# ):

#     res = requests.get(
#         "https://dkstatics-public.digikala.com/digikala-products/e6e05344b69bb6ee64ef0d14b9052f7c48ab968e_1695628552.jpg?x-oss-process=image/resize,m_lfit,h_800,w_800/quality,q_90")
#     with open("pic.jpg", "wb")as f:
#         f.write(res.content)
#     storage.add_file_to_s3("yechi.jpg", "pic.jpg", "sample")

#     os.remove("pic.jpg")
