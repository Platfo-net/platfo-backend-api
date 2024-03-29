import tiktoken
from langchain_community.document_loaders.pdf import PyPDFLoader, OnlinePDFLoader
from langchain_community.document_loaders.text import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_pdf_document(file):
    loader = PyPDFLoader(file)
    data = loader.load()
    return data


def load_text_document(file):
    loader = TextLoader(file)
    data = loader.load()
    return data


def chunk_data(data, chunk_size=256, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(data)
    return chunks


def print_embedding_cost(texts):
    enc = tiktoken.encoding_for_model('text-embedding-3-small')
    total_tokens = sum([len(enc.encode(page.page_content)) for page in texts])
    print(f'Total Tokens: {total_tokens}')
    print(f'Embedding Cost in USD: {total_tokens / 1000 * 0.00002:.6f}')