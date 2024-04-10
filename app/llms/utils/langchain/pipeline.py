from app.core.config import settings
from app.core.storage import download_file_from_minio
from app.llms.utils.dependencies import get_chroma_client
from app.llms.utils.langchain.helpers import get_document_loader_data, chunk_data, clear_text, get_chat_prompt, \
    create_llm_model
from app.llms.vectordb.chroma_client import ChromaClient


def load_knowledge_base_data(file_path: str):
    temp_file_path = download_file_from_minio(settings.S3_KNOWLEDGE_BASE_BUCKET, file_path)
    data = get_document_loader_data(file_path=file_path, file=temp_file_path)
    chunked_data = chunk_data(data)
    return chunked_data

def create_chain(setup_and_retrieval, output_parser):
    prompt = get_chat_prompt()
    llm = create_llm_model()
    chain = setup_and_retrieval | prompt | llm | output_parser
    return chain


def get_question_and_answer(question: str) -> str:
    from langchain.chains.retrieval_qa.base import RetrievalQA

    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name='3d8bf47b-f98c-4965-85ad-97c6e9265ea9')
    retriever = vector_db.search_embeddings()
    llm = create_llm_model()
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
    r = chain.invoke(question)
    print('result from the LLMMMMMM', r)
    return clear_text(r['result'])
