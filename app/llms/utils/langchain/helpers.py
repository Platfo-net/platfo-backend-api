import re
import uuid

import tiktoken
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI

from app.llms.utils import config


def generate_doc_ids(docs):
    return [str(uuid.uuid4()) for _ in docs]


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


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def extract_metadata(context: list[Document]):
    metadata_values = []
    for doc in context:
        metadata_values.extend(doc.metadata.values())
    return metadata_values


def get_chat_prompt():
    template = """
    {user_prompt}
    Question: {query}
    Context: {context}
    Answer:
    """

    prompt = ChatPromptTemplate.from_template(template)
    return prompt


def create_llm_model(temperature: float):
    return ChatOpenAI(openai_api_key=config.OPEN_API_KEY, model=config.LLM_MODEL,  # type: ignore
                      temperature=temperature)
