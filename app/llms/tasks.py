import logging

from app.core.celery import celery
from app.db.session import SessionLocal
from app.llms.utils.dependencies import get_chroma_client
from app.llms.utils.langchain.helpers import calculate_embedding_cost
from app.llms.utils.langchain.pipeline import load_knowledge_base_crawler_data, \
    load_knowledge_base_data, load_knowledge_base_manual_input_data
from app.llms.utils.monitoring import create_embedding_cost
from app.llms.vectordb.chroma_client import ChromaClient


@celery.task()
def embed_knowledge_base_document_task(file_path, collection_name, metadatas, knowledge_base_id):
    logging.info('Started the embedding knowledge base document task')
    db = SessionLocal()

    data = load_knowledge_base_data(file_path, [{"unique_identifier": metadatas}])
    total_tokens, cost_usd = calculate_embedding_cost(data)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_embeddings(data)

    db.close()
    logging.info('Finished the embedding knowledge base document task')


@celery.task()
def embed_knowledge_base_crawler_task(urls, collection_name, metadatas, knowledge_base_id):
    logging.info('Started the embedding knowledge base crawler task')
    db = SessionLocal()

    data = load_knowledge_base_crawler_data(urls, [metadatas])
    total_tokens, cost_usd = calculate_embedding_cost(data)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_embeddings(data)

    db.close()
    logging.info('Finished the embedding knowledge base crawler task')


@celery.task()
def embed_knowledge_base_manual_input_task(manual_input, collection_name, metadatas,
                                           knowledge_base_id):
    logging.info('Started the embedding knowledge base manual input task')
    db = SessionLocal()

    data = load_knowledge_base_manual_input_data(manual_input, [metadatas])
    total_tokens, cost_usd = calculate_embedding_cost(data)
    create_embedding_cost(db, total_tokens, cost_usd, knowledge_base_id)

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_embeddings(data)

    db.close()
    logging.info('Finished the embedding knowledge base manual input task')
