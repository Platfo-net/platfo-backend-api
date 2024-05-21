from abc import ABC, abstractmethod

from chromadb import ClientAPI
from langchain.retrievers import MultiVectorRetriever
from langchain.vectorstores.chroma import Chroma
from langchain_community.storage.redis import RedisStore
from langchain_openai import OpenAIEmbeddings

from app.api.deps import get_redis_client
from app.llms.utils import config


class BaseClient(ABC):
    """Abstract base class for client implementations."""

    @abstractmethod
    def store_embeddings(self, documents, ids=None):
        """Abstract method for storing embeddings."""
        ...

    @abstractmethod
    def search_embeddings(self, search_kwargs: dict):
        """Abstract method for searching embeddings."""
        ...


class ChromaClient(BaseClient):

    def __init__(self, client, collection_name):
        self._collection_name = collection_name
        self._chroma: ClientAPI = client
        self.client = Chroma(
            client=self._chroma,
            embedding_function=self.embedding,
            collection_name=self._collection_name,
        )
        self.multi_retriever_client = MultiVectorRetriever(
            vectorstore=self.client, byte_store=RedisStore(client=get_redis_client()),
            search_kwargs=config.SEARCH_RESULT_EMBEDDINGS_LOOKUPS)

    @property
    def embedding(self):
        return OpenAIEmbeddings(openai_api_key=config.OPEN_API_KEY,
                                model=config.EMBEDDING_MODEL)  # type: ignore

    def store_embeddings(self, documents, ids=None):
        return self.client.from_documents(documents, client=self._chroma, embedding=self.embedding,
                                          collection_name=self._collection_name, ids=ids)

    def search_embeddings(self, search_kwargs: dict = config.SEARCH_RESULT_EMBEDDINGS_LOOKUPS):
        return self.client.as_retriever(search_type='similarity', search_kwargs=search_kwargs)

    def store_multi_embeddings(self, documents, sub_documents, ids=None):
        self.multi_retriever_client.vectorstore.from_documents(
            sub_documents,
            client=self._chroma,
            embedding=self.embedding,
            collection_name=self._collection_name,
        )
        self.multi_retriever_client.docstore.mset(list(zip(ids, documents)))

    def search_multi_embeddings(self):
        return self.multi_retriever_client
