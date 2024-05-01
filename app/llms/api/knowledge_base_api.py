import uuid
from typing import List

from chromadb import ClientAPI
from fastapi import APIRouter, Depends, File, Security, UploadFile, status
from pydantic import UUID4

from app import models
from app.api import deps
from app.constants.role import Role
from app.core import storage
from app.core.config import settings
from app.core.storage import get_object_url
from app.llms.schemas.knowledge_base_schema import KnowledgeBase, KnowledgeBaseCreate, \
    KnowledgeBaseUpdate
from app.llms.services.chatbot_service import ChatBotService
from app.llms.services.knowledge_base_service import KnowledgeBaseService
from app.llms.tasks import embed_knowledge_base_crawler_task, embed_knowledge_base_document_task
from app.llms.utils.dependencies import get_chroma_client, get_service
from app.llms.utils.langchain.pipeline import get_question_and_answer
from app.schemas import FileUpload

router = APIRouter(
    prefix="/knowledge_base",
    tags=["Knowledge Base"],
)


@router.get('/all/{chatbot_id}', response_model=List[KnowledgeBase])
def get_knowledge_bases(
    chatbot_id: UUID4,
    knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    return knowledge_base_service.get_multi_by_chatbot_id(chatbot_id=chatbot_id,
                                                          current_user=current_user)


@router.get('/{id}', response_model=KnowledgeBase)
def get_knowledge_base(
    id: UUID4,
    knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    knowledge_base = knowledge_base_service.validator.validate_exists(uuid=id, model=KnowledgeBase)
    knowledge_base_service.validator.validate_user_ownership(obj=knowledge_base.chatbot,
                                                             current_user=current_user)
    knowledge_base = knowledge_base_service.get_by_uuid(uuid=id)
    knowledge_base.chatbot_id = knowledge_base.chatbot.uuid
    knowledge_base.file_url = get_object_url(knowledge_base.file_path,
                                             settings.S3_KNOWLEDGE_BASE_BUCKET)
    return knowledge_base


@router.post('', response_model=KnowledgeBase)
def create_knowledge_base(
    obj_in: KnowledgeBaseCreate,
    knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    collection_name = str(obj_in.chatbot_id)
    new_knowledge_base = knowledge_base_service.create(obj_in, current_user)
    new_knowledge_base.file_url = get_object_url(new_knowledge_base.file_path,
                                                 settings.S3_KNOWLEDGE_BASE_BUCKET)

    embed_knowledge_base_document_task.delay(new_knowledge_base.file_path, collection_name,
                                             new_knowledge_base.metadatas, new_knowledge_base.id)

    return new_knowledge_base


@router.post('/crawler', response_model=KnowledgeBase)
def create_knowledge_base_crawler(
    obj_in: KnowledgeBaseCreate,
    knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    collection_name = str(obj_in.chatbot_id)
    new_knowledge_base = knowledge_base_service.create(obj_in, current_user)

    embed_knowledge_base_crawler_task.delay(new_knowledge_base.urls, collection_name,
                                            new_knowledge_base.metadatas, new_knowledge_base.id)

    return new_knowledge_base


@router.get('/{id}', response_model=KnowledgeBase)
def update_knowledge_base_crawler(
    id: UUID4,
    obj_in: KnowledgeBaseUpdate,
    knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
    chroma: ClientAPI = Depends(get_chroma_client),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    knowledge_base = knowledge_base_service.validator.validate_exists(uuid=id, model=KnowledgeBase)
    knowledge_base_service.validator.validate_user_ownership(obj=knowledge_base.chatbot,
                                                             current_user=current_user)

    updated_knowledge_base = knowledge_base_service.update(knowledge_base, obj_in)
    knowledge_base_service.remove_with_embeddings(knowledge_base, chroma)
    embed_knowledge_base_crawler_task.delay(updated_knowledge_base.urls, str(obj_in.chatbot_id),
                                            updated_knowledge_base.metadatas,
                                            updated_knowledge_base.id)
    return updated_knowledge_base


@router.get('/question/chatbot_id/ask')
def ask_question(
    question: str,
    chatbot_id: int,
    chatbot_service: ChatBotService = Depends(get_service(ChatBotService)),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    r = get_question_and_answer(question, chatbot_id, chatbot_service)
    return {"answer": r}


@router.post("/upload/", response_model=FileUpload)
def upload_knowledge_base_file(
    file: UploadFile = File(...),
    _: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.USER["name"], Role.DEVELOPER["name"], ],
    ),
):
    filename = f"{uuid.uuid4()}-{file.filename}"
    uploaded_file_name = storage.add_file_to_s3(filename, file.file.fileno(),
                                                settings.S3_KNOWLEDGE_BASE_BUCKET)

    return storage.get_file(uploaded_file_name, settings.S3_KNOWLEDGE_BASE_BUCKET)


@router.put('/{id}', response_model=KnowledgeBase)
def update_knowledge_base(
    id: UUID4,
    obj_in: KnowledgeBaseUpdate,
    knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    knowledge_base = knowledge_base_service.validator.validate_exists(uuid=id, model=KnowledgeBase)
    knowledge_base_service.validator.validate_user_ownership(obj=knowledge_base.chatbot,
                                                             current_user=current_user)

    updated_knowledge_base = knowledge_base_service.update(knowledge_base, obj_in)
    updated_knowledge_base.chatbot_id = updated_knowledge_base.chatbot.uuid
    updated_knowledge_base.file_url = get_object_url(updated_knowledge_base.file_path,
                                                     settings.S3_KNOWLEDGE_BASE_BUCKET)
    return updated_knowledge_base


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base(
    id: UUID4,
    knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
    chroma: ClientAPI = Depends(get_chroma_client),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Role.USER['name'], Role.ADMIN['name'], Role.DEVELOPER['name'], ],
    ),
):
    knowledge_base = knowledge_base_service.validator.validate_exists(uuid=id, model=KnowledgeBase)
    knowledge_base_service.validator.validate_user_ownership(obj=knowledge_base.chatbot,
                                                             current_user=current_user)
    return knowledge_base_service.remove_with_embeddings(knowledge_base, chroma)
