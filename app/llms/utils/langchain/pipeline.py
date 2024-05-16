from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from app.core.config import settings
from app.core.storage import download_file_from_minio
from app.llms.models import ChatBot
from app.llms.services.chatbot_service import ChatBotService
from app.llms.services.knowledge_base_service import KnowledgeBaseService
from app.llms.utils.dependencies import get_chroma_client
from app.llms.utils.langchain.helpers import chunk_data, clear_text, create_llm_model, \
    extract_metadata, format_docs, get_chat_prompt, get_crawler_loader_data, \
    get_document_loader_data, get_manual_input_loader_data
from app.llms.vectordb.chroma_client import ChromaClient


def load_knowledge_base_data(file_path: str, metadatas: list[dict]):
    temp_file_path = download_file_from_minio(settings.S3_KNOWLEDGE_BASE_BUCKET, file_path)
    data = get_document_loader_data(file_path=file_path, file=temp_file_path)
    chunked_data = chunk_data(data, metadatas)
    return chunked_data


def load_knowledge_base_crawler_data(urls: list[str], metadatas: list[dict]):
    data = get_crawler_loader_data(urls=urls)
    chunked_data = chunk_data(data, metadatas)
    return chunked_data


def load_knowledge_base_manual_input_data(manual_input: str, metadatas: list[dict]):
    chunked_data = get_manual_input_loader_data([manual_input], metadatas)
    return chunked_data


def rag_chain_with_source(retriever, prompt_callable, rag_chain_from_docs):
    setup_and_retrieval = RunnableParallel({
        "context": retriever,
        "query": RunnablePassthrough(),
        "user_prompt": RunnableLambda(prompt_callable)
    }).assign(answer=rag_chain_from_docs)
    return setup_and_retrieval


def setup_rag_chain_from_docs(output_parser, temperature):
    llm = create_llm_model(temperature)
    prompt = get_chat_prompt()
    chain = RunnablePassthrough.assign(
        context=(lambda x: format_docs(x["context"]))) | prompt | llm | output_parser
    return chain


def get_question_and_answer(question: str, chatbot_id: int, chatbot_service: ChatBotService,
                            knowledge_base_service: KnowledgeBaseService):
    from langchain_core.output_parsers import StrOutputParser
    chatbot = chatbot_service.validator.validate_exists_with_id(pk=chatbot_id, model=ChatBot)
    chroma = get_chroma_client()
    vector_db = ChromaClient(client=chroma, collection_name=str(chatbot.uuid))
    retriever = vector_db.search_embeddings()
    setup_and_retrieval = setup_rag_chain_from_docs(StrOutputParser(), chatbot.temperature)
    chain = rag_chain_with_source(retriever, lambda _: chatbot.prompt, setup_and_retrieval)
    answer_with_source = chain.invoke(question)
    context = answer_with_source.get("context")
    answer = answer_with_source.get("answer")

    metadata_values = [extract_metadata(context)[0]]

    print(f"Extracted metadata values are: {metadata_values}")
    knowledge_bases = knowledge_base_service.get_by_metadata_values(chatbot_id, metadata_values)
    print(f"Knowledge bases objects are: {knowledge_bases}")
    print(f"Question: {question}, Chatbot ID: {chatbot_id}, Answer: {answer}, Context: {context}")
    return clear_text(answer), knowledge_bases
