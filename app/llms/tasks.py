import logging

from app.core.celery import celery
from app.llms.utils.dependencies import get_chroma_client
from app.llms.utils.langchain.pipeline import load_knowledge_base_data

from app.llms.vectordb.chroma_client import ChromaClient


@celery.task()
def embed_knowledge_base_document_task(file_path, collection_name):
    logging.info('helloooooooooooo')
    data = load_knowledge_base_data(file_path)
    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=collection_name)
    vector_db.store_embeddings(data)
    logging.info('byeeeeeeeeeeeeeee')

