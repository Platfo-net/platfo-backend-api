from abc import ABC, abstractmethod

from chromadb import ClientAPI
from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings

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
        self.client = Chroma(client=self._chroma,
                             embedding_function=self.embedding,
                             collection_name=self._collection_name,
                             )

    @property
    def embedding(self):
        return OpenAIEmbeddings(openai_api_key=config.OPEN_API_KEY) # type: ignore

    def store_embeddings(self, documents, ids=None):
        return self.client.from_documents(documents, client=self._chroma, embedding=self.embedding,
                                          collection_name=self._collection_name, ids=ids)

    def search_embeddings(self, search_kwargs: dict = config.MAX_SEARCH_RESULT_EMBEDDINGS):
        return self.client.as_retriever(search_type='similarity', sesearch_kwargs=search_kwargs)
