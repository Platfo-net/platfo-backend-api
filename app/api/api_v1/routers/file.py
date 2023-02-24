import uuid

from fastapi import UploadFile, File, APIRouter, Security

from app import models
from app import schemas
from app.api import deps
from app.constants.role import Role
from app.core import storage
from app.core.config import settings

router = APIRouter(prefix="/file", tags=["File"])


@router.post("/upload/postman/campaign", response_model=schemas.Image)
async def upload_postman_campaign_image(
        file: UploadFile = File(...),
        _: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.ADMIN["name"],
            ],
        ),
):
    filename = f"{uuid.uuid4()}-{file.filename}"
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_CAMPAIGN_BUCKET
    )

    return storage.get_file(uploaded_file_name, settings.S3_CAMPAIGN_BUCKET)
