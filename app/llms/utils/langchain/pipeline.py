from app.core.config import settings
from app.core.storage import download_file_from_minio
from app.llms.utils.dependencies import get_chroma_client
from app.llms.utils.langchain.helpers import get_document_loader_data, chunk_data, clear_text, get_chat_prompt, \
    create_llm_model, create_setup_retriever
from app.llms.vectordb.chroma_client import ChromaClient


def load_knowledge_base_data(file_path: str, metadatas: list[dict]):
    temp_file_path = download_file_from_minio(settings.S3_KNOWLEDGE_BASE_BUCKET, file_path)
    data = get_document_loader_data(file_path=file_path, file=temp_file_path)
    chunked_data = chunk_data(data, metadatas)
    return chunked_data


def create_chain(setup_and_retrieval, output_parser):
    prompt = get_chat_prompt()
    llm = create_llm_model()
    chain = setup_and_retrieval | prompt | llm | output_parser
    return chain


def get_question_and_answer(question: str, prompt: str = "") -> str:
    from langchain_core.output_parsers import StrOutputParser

    chroma = get_chroma_client()
    # for dev test
    vector_db = ChromaClient(client=chroma, collection_name='3d8bf47b-f98c-4965-85ad-97c6e9265ea9')
    # for local test
    # vector_db = ChromaClient(client=chroma, collection_name='439f6529-cc49-43fc-9194-f8324d442b76')
    retriever = vector_db.search_embeddings()
    output_parser = StrOutputParser()
    setup_and_retrieval = create_setup_retriever(retriever,
                                                 lambda _: prompt)
    chain = create_chain(setup_and_retrieval, output_parser)
    r = chain.invoke(question)
    print('Result from the llm model', r)
    return clear_text(r)
