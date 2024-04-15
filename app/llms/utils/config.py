import os

from dotenv import load_dotenv

load_dotenv()

MAX_SEARCH_RESULT_EMBEDDINGS = {"k": 8}

OPEN_API_KEY = os.environ.get("OPEN_API_KEY", "")
LLM_MODEL = 'gpt-3.5-turbo'


class ChromaConfig:
    HOST: str = os.getenv('CHROMADB_HOST', 'localhost')
    PORT: int = int(os.getenv('CHROMADB_PORT', '8005'))
    CHROMADB_TOKEN = os.environ.get("CHROMADB_TOKEN", "")
    CHROMA_CLIENT_AUTH_PROVIDER = os.environ.get("CHROMA_CLIENT_AUTH_PROVIDER", "")

