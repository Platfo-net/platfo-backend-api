from uuid import uuid4

from langchain.vectorstores.chroma import Chroma
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.llms.utils import config


class ChromaClient:

    def __init__(self, chroma, persist_directory='.',
                 embedding_function=OpenAIEmbeddings(openai_api_key=config.OPEN_API_KEY)):
        self._chroma = chroma
        self.client = Chroma(client=chroma,
                             persist_directory=persist_directory,
                             embedding_function=embedding_function
                             )

    def store_embeddings(self, documents, ids=None):
        if ids is None:
            ids = [str(uuid4()) for _ in documents]
        return self.client.from_documents(documents, ids=ids)

    def search_embeddings(self, search_kwargs: dict = config.MAX_SEARCH_RESULT_EMBEDDINGS):
        return self.client.as_retriever(search_kwargs=search_kwargs)
