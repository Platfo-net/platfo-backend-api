from app.llms.models.knowledge_base import KnowledgeBase
from app.llms.repository.base_repository import CRUDBRepository


class KnowledgeBaseRepository(CRUDBRepository):
    model = KnowledgeBase
