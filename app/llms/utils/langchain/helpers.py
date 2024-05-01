import os
import re

import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_openai.chat_models import ChatOpenAI

from app.llms.utils import config


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


def chunk_data(data, metadatas, chunk_size=256, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                   chunk_overlap=chunk_overlap)
    texts = [d.page_content for d in data]
    metadatas = metadatas * len(texts)
    chunks = text_splitter.create_documents(texts=texts, metadatas=metadatas)
    return chunks


def calculate_embedding_cost(texts):
    enc = tiktoken.encoding_for_model('text-embedding-3-small')
    total_tokens = sum([len(enc.encode(page.page_content)) for page in texts])
    cost_per_million_tokens = 0.02
    cost_usd = total_tokens / 1_000_000 * cost_per_million_tokens
    print(f'Total Tokens: {total_tokens}')
    print(f'Embedding Cost in USD (per million tokens): {cost_usd:.6f}')
    return total_tokens, cost_usd


def clear_text(text):
    # Remove newlines (\n)
    text = text.replace("\n", " ")
    # Remove unnecessary punctuation
    text = re.sub("[^\w\s]", "", text)  # noqa

    return text


def get_chat_prompt():
    template = """
    Context: {context}
    {user_prompt}
    Question: {query}
    """

    prompt = ChatPromptTemplate.from_template(template)
    return prompt


def create_setup_retriever(retriever, prompt_callable):
    setup_and_retrieval = RunnableParallel({
        "context": retriever,
        "query": RunnablePassthrough(),
        "user_prompt": RunnableLambda(prompt_callable)
    })
    return setup_and_retrieval


def create_llm_model(temperature: float):
    return ChatOpenAI(openai_api_key=config.OPEN_API_KEY, model=config.LLM_MODEL,  # type: ignore
                      temperature=temperature)
