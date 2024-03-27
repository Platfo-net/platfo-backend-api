import os

from dotenv import load_dotenv

load_dotenv()

MAX_SEARCH_RESULT_EMBEDDINGS = {"k": 4}


class ChromaConfig:
    HOST: str = os.getenv('CHROMADB_HOST', 'localhost')
    PORT: int = int(os.getenv('CHROMADB_PORT', '8005'))
