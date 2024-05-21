import os

from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader


class DocumentFormat:
    PDF = ".pdf"
    TXT = ".txt"


def load_pdf_document(file):
    try:
        loader = PyPDFLoader(file)
        return loader.load()
    except Exception as e:
        raise e


def load_text_document(file):
    try:
        loader = TextLoader(file)
        return loader.load()
    except Exception as e:
        raise e


def get_document_loader_data(file_path, file):
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    loaders = {DocumentFormat.PDF: load_pdf_document, DocumentFormat.TXT: load_text_document, }
    loader_func = loaders.get(extension)
    return loader_func(file)


def get_crawler_loader_data(urls: list[str]):
    from langchain_community.document_loaders.async_html import AsyncHtmlLoader
    from langchain_community.document_transformers.beautiful_soup_transformer import \
        BeautifulSoupTransformer

    loader = AsyncHtmlLoader(urls)
    docs = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    transformed_docs = bs_transformer.transform_documents(docs)
    return transformed_docs
