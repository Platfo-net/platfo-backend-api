import os

from dotenv import load_dotenv

load_dotenv()

MAX_SEARCH_RESULT_EMBEDDINGS = {"k": 4}

OPEN_API_KEY = os.environ.get("OPEN_API_KEY", "")


class ChromaConfig:
    HOST: str = os.getenv('CHROMADB_HOST', 'localhost')
    PORT: int = int(os.getenv('CHROMADB_PORT', '8005'))
