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
