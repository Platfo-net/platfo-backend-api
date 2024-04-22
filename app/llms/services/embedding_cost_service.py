from app.llms.repository.embedding_cost_repository import EmbeddingCostRepository
from app.llms.services.base_service import BaseService


class EmbeddingCostService(BaseService):

    def __init__(self, embedding_cost_repo: EmbeddingCostRepository):
        self.embedding_cost_repo = embedding_cost_repo
        super().__init__(embedding_cost_repo)
