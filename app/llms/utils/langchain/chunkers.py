from abc import ABC, abstractmethod

from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingStrategy(ABC):
    """
    Abstract base class defining the interface for chunking strategies.
    """

    @abstractmethod
    def chunk(self, data, metadatas, doc_ids):
        """
        This method defines the abstract contract for chunking text data.
        Subclasses must implement this logic.
        """
        pass


class RecursiveChunkingStrategy(ChunkingStrategy):
    """
    Concrete chunking strategy for recursive character based splitting.
    """

    def __init__(self, chunk_size=600, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, data, metadatas, doc_ids):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,
                                                       chunk_overlap=self.overlap)
        texts = [d.page_content for d in data]
        metadatas = metadatas * len(texts)
        return text_splitter.create_documents(texts=texts, metadatas=metadatas)


class ManualInputChunkingStrategy(ChunkingStrategy):
    """
    Concrete chunking strategy for manual input data with specific chunk_size and overlap.
    """

    def __init__(self, chunk_size=1000, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, texts, metadatas, doc_ids):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,
                                                       chunk_overlap=self.overlap)
        metadatas = metadatas * len(texts)
        return text_splitter.create_documents(texts=texts, metadatas=metadatas)


class ParentMultiVectorChunkingStrategy(RecursiveChunkingStrategy):
    """
    Concrete chunking strategy for parent multi-vector data with a specific chunk_size.
    """

    def __init__(self):
        super().__init__(chunk_size=1000)


class ChildMultiVectorChunkingStrategy(ChunkingStrategy):
    """
    Concrete chunking strategy for child multi-vector data with a different approach.
    """

    def __init__(self):
        self.child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=200)
        self.id_key = "doc_id"

    def chunk(self, data, metadatas, doc_ids):
        id_key = "doc_id"
        sub_docs = []
        for i, doc in enumerate(data):
            _id = doc_ids[i]
            _sub_docs = self.child_text_splitter.split_documents([doc])
            for _doc in _sub_docs:
                _doc.metadata[id_key] = _id
            sub_docs.extend(_sub_docs)
        return sub_docs


class Chunker:
    """
    Class utilizing the chunking strategies.
    """

    def __init__(self, chunking_strategy: ChunkingStrategy):
        self.chunking_strategy = chunking_strategy

    def chunk(self, data, metadatas=None, doc_ids=None):
        """
        Delegates chunking logic to the chosen strategy.
        """
        return self.chunking_strategy.chunk(data, metadatas, doc_ids)

    def set_dynamic_chunking_strategy(self, chunking_strategy: ChunkingStrategy):
        """
        Allows dynamic strategy switching for the chunker.
        """
        self.chunking_strategy = chunking_strategy
