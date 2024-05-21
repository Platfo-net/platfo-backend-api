import logging

from app.core.celery import celery
from app.core.config import settings
from app.core.utils import decrease_cost_from_credit
from app.db.session import SessionLocal
from app.llms.repository.credit_repository import UserChatBotCreditRepository
from app.llms.services.credit_service import UserChatBotCreditService
from app.llms.utils.dependencies import get_chroma_client
from app.llms.utils.langchain.helpers import calculate_embedding_cost
from app.llms.utils.langchain.pipeline import load_knowledge_base_crawler_data, \
    load_knowledge_base_crawler_data_multi_vector, load_knowledge_base_data_file, \
    load_knowledge_base_data_file_multi_vector, load_knowledge_base_manual_input_data, \
    load_knowledge_base_manual_input_data_multi_vector
from app.llms.utils.monitoring import create_embedding_cost
from app.llms.vectordb.chroma_client import ChromaClient


@celery.task()
def embed_knowledge_base_document_task(file_path, collection_name, unique_identifier,
                                       knowledge_base_id, user_id):
    logging.info('Started the embedding knowledge base document task')
    db = SessionLocal()

    data = load_knowledge_base_data_file(file_path, [unique_identifier])
    total_tokens, cost_usd = calculate_embedding_cost(data)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)
    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_embeddings(data)
    credit_service = UserChatBotCreditService(UserChatBotCreditRepository(db))
    decrease_cost_from_credit(credit_service, user_id,
                              int(settings.CHATBOT_TOKEN_COST * total_tokens))

    db.close()
    (logging.info('Finished the embedding knowledge base document task'))


@celery.task()
def embed_knowledge_base_multi_vector_document_task(file_path, collection_name, unique_identifier,
                                                    knowledge_base_id):
    logging.info('Started the embedding knowledge base multi vector document task')
    db = SessionLocal()
    documents, sub_documents, doc_ids = load_knowledge_base_data_file_multi_vector(
        file_path, [unique_identifier])
    total_tokens, cost_usd = calculate_embedding_cost(documents)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_multi_embeddings(documents=documents, sub_documents=sub_documents, ids=doc_ids)

    db.close()
    logging.info('Finished the embedding knowledge base multi vector document task')


@celery.task()
def embed_knowledge_base_crawler_task(urls, collection_name, unique_identifier, knowledge_base_id,
                                      user_id):
    logging.info('Started the embedding knowledge base crawler task')
    db = SessionLocal()

    data = load_knowledge_base_crawler_data(urls, [unique_identifier])
    total_tokens, cost_usd = calculate_embedding_cost(data)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_embeddings(data)

    credit_service = UserChatBotCreditService(UserChatBotCreditRepository(db))
    decrease_cost_from_credit(credit_service, user_id,
                              int(settings.CHATBOT_TOKEN_COST * total_tokens))

    db.close()
    logging.info('Finished the embedding knowledge base crawler task')


@celery.task()
def embed_knowledge_base_multi_vector_crawler_task(urls, collection_name, unique_identifier,
                                                   knowledge_base_id, user_id):
    logging.info('Started the embedding knowledge base multi vector crawler task')
    db = SessionLocal()

    documents, sub_documents, doc_ids = load_knowledge_base_crawler_data_multi_vector(
        urls, [unique_identifier])
    total_tokens, cost_usd = calculate_embedding_cost(documents)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_multi_embeddings(documents=documents, sub_documents=sub_documents, ids=doc_ids)

    credit_service = UserChatBotCreditService(UserChatBotCreditRepository(db))
    decrease_cost_from_credit(credit_service, user_id,
                              int(settings.CHATBOT_TOKEN_COST * total_tokens))

    db.close()
    logging.info('Finished the embedding knowledge base multi vector crawler task')


@celery.task()
def embed_knowledge_base_manual_input_task(manual_input, collection_name, unique_identifier,
                                           knowledge_base_id, user_id):
    logging.info('Started the embedding knowledge base manual input task')
    db = SessionLocal()

    data = load_knowledge_base_manual_input_data(manual_input, [unique_identifier])
    total_tokens, cost_usd = calculate_embedding_cost(data)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_embeddings(data)
    credit_service = UserChatBotCreditService(UserChatBotCreditRepository(db))
    decrease_cost_from_credit(credit_service, user_id,
                              int(settings.CHATBOT_TOKEN_COST * total_tokens))

    db.close()
    logging.info('Finished the embedding knowledge base manual input task')


@celery.task()
def embed_knowledge_base_multi_vector_manual_input_task(manual_input, collection_name,
                                                        unique_identifier, knowledge_base_id):
    logging.info('Started the embedding knowledge base multi vector manual input task')
    db = SessionLocal()

    documents, sub_documents, doc_ids = load_knowledge_base_manual_input_data_multi_vector(
        manual_input, [unique_identifier])
    total_tokens, cost_usd = calculate_embedding_cost(documents)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_multi_embeddings(documents=documents, sub_documents=sub_documents, ids=doc_ids)

    db.close()
    logging.info('Finished the embedding knowledge base multi vector manual input task')
