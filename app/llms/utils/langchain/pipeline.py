from app.core.config import settings
from app.core.storage import download_file_from_minio
from app.llms.utils.dependencies import get_chroma_client
from app.llms.utils.langchain.helpers import get_document_loader_data, chunk_data, clear_text
from app.llms.vectordb.chroma_client import ChromaClient


def load_knowledge_base_data(file_path: str):
    temp_file_path = download_file_from_minio(settings.S3_KNOWLEDGE_BASE_BUCKET, file_path)
    data = get_document_loader_data(file_path=file_path, file=temp_file_path)
    chunked_data = chunk_data(data)
    return chunked_data


def get_question_and_answer(question: str) -> str:
    from langchain_openai.chat_models import ChatOpenAI
    from langchain.chains.retrieval_qa.base import RetrievalQA

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name='3d8bf47b-f98c-4965-85ad-97c6e9265ea9')
    re = vector_db.search_embeddings()
    llm = ChatOpenAI(openai_api_key="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", model='gpt-3.5-turbo')
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=re)
    r = chain.invoke(question)
    print('result from the LLMMMMMM', r)
    return clear_text(r['result'])
