from app.core.config import settings
from app.core.storage import download_file_from_minio
from app.llms.utils.langchain.helpers import get_document_loader_data, chunk_data


def load_knowledge_base_data(file_path: str):
    temp_file_path = download_file_from_minio(settings.S3_KNOWLEDGE_BASE_BUCKET, file_path)
    data = get_document_loader_data(file_path=file_path, file=temp_file_path)
    chunked_data = chunk_data(data)
    return chunked_data
