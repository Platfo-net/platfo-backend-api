import uuid
from typing import List

from chromadb import ClientAPI
from fastapi import Security, APIRouter, UploadFile, File, Depends, status
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.chat_models.openai import ChatOpenAI
from pydantic import UUID4

from app import models
from app.api import deps
from app.constants.role import Role
from app.core import storage
from app.core.config import settings
from app.core.storage import download_file_from_minio
from app.llms.schemas.knowledge_base_schema import KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate
from app.llms.services.knowledge_base_service import KnowledgeBaseService
from app.llms.utils.dependencies import get_service, get_chroma_client
from app.llms.utils.langchain.helpers import chunk_data, load_text_document
from app.llms.vectordb.chroma_client import ChromaClient
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
            scopes=[
                Role.USER['name'],
                Role.ADMIN['name'],
                Role.DEVELOPER['name'],
            ],
        ),
):
    return knowledge_base_service.get_list_by_chatbot_id(chatbot_id=chatbot_id,
                                                         current_user=current_user)


@router.get('/{id}', response_model=KnowledgeBase)
def get_knowledge_base(
        id: UUID4,
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
    knowledge_base = knowledge_base_service.validator.validate_exists(uuid=id)
    knowledge_base_service.validator.validate_user_ownership(obj=knowledge_base.chatbot,
                                                             current_user=current_user)
    knowledge_base = knowledge_base_service.get_by_uuid(uuid=id)
    knowledge_base.chatbot_id = knowledge_base.chatbot.uuid
    return knowledge_base


@router.post('', response_model=KnowledgeBase)
def create_knowledge_base(
        obj_in: KnowledgeBaseCreate,
        chroma: ClientAPI = Depends(get_chroma_client),
        knowledge_base_service: KnowledgeBaseService = Depends(get_service(KnowledgeBaseService)),
        _: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER['name'],
                Role.ADMIN['name'],
                Role.DEVELOPER['name'],
            ],
        ),
):
    collection_name = str(obj_in.chatbot_id)
    new_knowledge_base = knowledge_base_service.add(obj_in)
    file_content = download_file_from_minio(settings.S3_KNOWLEDGE_BASE_BUCKET, new_knowledge_base.file_path)
    # data = load_pdf_document(file_content)
    data = load_text_document(file_content)
    chunked_data = chunk_data(data)
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_embeddings(chunked_data)
    print('2222', vector_db._chroma.list_collections())
    print('3333', chroma.list_collections())
    print(chroma.get_collection(name=collection_name).count())

    return new_knowledge_base


@router.post('/test/')
def test(
        chroma: ClientAPI = Depends(get_chroma_client),
        _: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER['name'],
                Role.ADMIN['name'],
                Role.DEVELOPER['name'],
            ],
        ),
):
    vector_db = ChromaClient(client=chroma, collection_name='439f6529-cc49-43fc-9194-f8324d442b76')
    # print('6666', vector_db._chroma.list_collections())
    # print('8888', chroma.list_collections())
    # print(chroma.get_collection(name='439f6529-cc49-43fc-9194-f8324d442b76').count())
    # c = vector_db._chroma.list_collections()
    # c = chroma.list_collections()
    # print('111', c)
    # chroma.delete_collection(c[0].name)
    # print(chroma.list_collections())
    # print('333333', vector_db.client.get())
    # print(c.get())

    re = vector_db.search_embeddings()
    llm = ChatOpenAI(openai_api_key="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", model='gpt-3.5-turbo',
                     temperature=0.2)
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=re)
    r = chain.run('what is section one of it?')
    return r


@router.post("/upload/", response_model=FileUpload)
def upload_knowledge_base_file(
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
        filename, file.file.fileno(), settings.S3_KNOWLEDGE_BASE_BUCKET
    )

    return storage.get_file(uploaded_file_name, settings.S3_KNOWLEDGE_BASE_BUCKET)


@router.put('/{id}', response_model=KnowledgeBase)
def update_knowledge_base(
        id: UUID4,
        obj_in: KnowledgeBaseUpdate,
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
    knowledge_base = knowledge_base_service.validator.validate_exists(uuid=id)
    knowledge_base_service.validator.validate_user_ownership(obj=knowledge_base.chatbot,
                                                             current_user=current_user)

    updated_knowledge_base = knowledge_base_service.update(knowledge_base, obj_in)
    updated_knowledge_base.chatbot_id = updated_knowledge_base.chatbot.uuid
    return updated_knowledge_base


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base(
        id: UUID4,
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
    knowledge_base = knowledge_base_service.validator.validate_exists(uuid=id)
    knowledge_base_service.validator.validate_user_ownership(obj=knowledge_base.chatbot,
                                                             current_user=current_user)
    return knowledge_base_service.remove(knowledge_base.id)
