from pydantic import UUID4

from app.core.config import settings
from app.core.storage import download_file_from_minio
from app.db.session import SessionLocal
from app.llms.repository.chatbot_repository import ChatBotRepository
from app.llms.services.chatbot_service import ChatBotService
from app.llms.utils.dependencies import get_chroma_client
from app.llms.utils.langchain.helpers import chunk_data, clear_text, create_llm_model, \
    create_setup_retriever, get_chat_prompt, get_document_loader_data
from app.llms.vectordb.chroma_client import ChromaClient


def load_knowledge_base_data(file_path: str, metadatas: list[dict]):
    temp_file_path = download_file_from_minio(settings.S3_KNOWLEDGE_BASE_BUCKET, file_path)
    data = get_document_loader_data(file_path=file_path, file=temp_file_path)
    chunked_data = chunk_data(data, metadatas)
    return chunked_data


def create_chain(setup_and_retrieval, output_parser, temperature):
    llm = create_llm_model(temperature)
    prompt = get_chat_prompt()
    chain = setup_and_retrieval | prompt | llm | output_parser
    return chain


def get_question_and_answer(question: str, chatbot_id: UUID4) -> str:
    from langchain_core.output_parsers import StrOutputParser

    chatbot_service = ChatBotService(ChatBotRepository(SessionLocal()))
    chatbot = chatbot_service.validator.validate_exists(uuid=chatbot_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=str(chatbot.uuid))
    retriever = vector_db.search_embeddings()

    setup_and_retrieval = create_setup_retriever(retriever, lambda _: chatbot.prompt)
    chain = create_chain(setup_and_retrieval, StrOutputParser(), chatbot.temperature)
    answer = chain.invoke(question)
    print(f"Question: {question}, Chatbot ID: {chatbot_id}, Answer: {answer}")
    return clear_text(answer)
