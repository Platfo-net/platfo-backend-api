from sqlalchemy.orm import Session

from app.llms.repository.embedding_cost_repository import EmbeddingCostRepository
from app.llms.schemas.embedding_cost_schema import EmbeddingCostCreate
from app.llms.services.embedding_cost_service import EmbeddingCostService


def create_embedding_cost(db: Session, total_token, cost_usd, knowledgebase_id):
    embedding_cost_service = EmbeddingCostService(EmbeddingCostRepository(db))
    schema = EmbeddingCostCreate()
    schema.total_tokens = total_token
    schema.cost_usd = cost_usd
    schema.knowledgebase_id = knowledgebase_id

    embedding_cost_service.add(schema=schema)
