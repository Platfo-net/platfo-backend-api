from fastapi import UploadFile, File, APIRouter, Security
from app import models
from app.api import deps
from app.constants.role import Role
import uuid
from app.core import storage
from app.core.config import settings


router = APIRouter(prefix="/file", tags=["File"])


# @router.post("/upload/profile")
# async def upload_profile(
#         file: UploadFile = File(...),
#         current_user: models.User = Security(
#         deps.get_current_active_user,
#         scopes=[
#             Role.ADMIN["name"],
#             Role.USER["name"],
#         ],
#         ),
# ):
#     """
#         Service for uploading file and return url
#     """
#     filename = f'{uuid.uuid4()}-{file.filename}'
#     uploaded_file_name = storage.add_file_to_s3(
#         filename, file.file.fileno(), settings.S3_PROFILE_BUCKET)

#     url = storage.get_object_url(
#         uploaded_file_name, settings.S3_PROFILE_BUCKET)
#     return {"file_name": uploaded_file_name, "url": url}


@router.post("/upload/academy/attachment")
async def upload_academy_content_attachment(
        file: UploadFile = File(...),
        current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
        ],
        ),
):
    """
        Service for uploading file for academy 
        content attachements and return url
    """
    filename = f'{uuid.uuid4()}-{file.filename}'
    uploaded_file_name = storage.add_file_to_s3(
        filename, file.file.fileno(), settings.S3_ACADEMY_ATTACHMENT_BUCKET)

    url = storage.get_object_url(
        uploaded_file_name, settings.S3_ACADEMY_ATTACHMENT_BUCKET)
    return {"file_name": uploaded_file_name, "url": url}



@router.get("/upload/academy/attachment/{attachment_id}")
async def upload_academy_content_attachment(
        *,
        attachment_id:str,
        current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
        ],
        ),
):
    """
        Service for uploading file for academy 
        content attachements and return url
    """
    url = storage.get_object_url(attachment_id , settings.S3_ACADEMY_ATTACHMENT_BUCKET)

    return {"file_name": attachment_id, "url": url}
