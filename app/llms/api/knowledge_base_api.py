import uuid

from fastapi import Security, APIRouter, UploadFile, File, Depends

from app import models
from app.api import deps
from app.constants.role import Role
from app.core import storage
from app.core.config import settings
from app.llms.schemas.knowledge_base_schema import KnowledgeBase, KnowledgeBaseCreate
from app.llms.services.knowledge_base_service import KnowledgeBaseService
from app.llms.utils.dependencies import get_service
from app.schemas.file import FileUpload

router = APIRouter(
    prefix="/knowledge_base",
    tags=["Knowledge Base"],
)


@router.post('', response_model=KnowledgeBase)
def create_knowledge_base(
        obj_in: KnowledgeBaseCreate,
        knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER['name'],
                Role.ADMIN['name'],
                Role.DEVELOPER['name'],
            ],
        ),
):
    return knowledge_base_service.add(obj_in)


@router.post("/upload/", response_model=FileUpload)
async def upload_knowledge_base_file(
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

    return storage.get_file(uploaded_file_name, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)
