from app.llms.repository.knowledge_base_repository import KnowledgeBaseRepository
from app.llms.services.base_service import BaseService


class KnowledgeBaseService(BaseService):

    def __init__(self, knowledge_base_repo: KnowledgeBaseRepository):
        self.knowledge_base_repo = knowledge_base_repo
        super().__init__(knowledge_base_repo)

