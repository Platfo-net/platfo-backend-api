from app.llms.models.embedding_cost import EmbeddingCost
from app.llms.repository.base_repository import CRUDBRepository


class EmbeddingCostRepository(CRUDBRepository):
    model = EmbeddingCost
