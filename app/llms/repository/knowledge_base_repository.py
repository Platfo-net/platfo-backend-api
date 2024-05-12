from app.llms.models.knowledge_base import KnowledgeBase
from app.llms.repository.base_repository import CRUDBRepository


class KnowledgeBaseRepository(CRUDBRepository):
    model = KnowledgeBase

    def get_multi_by_chatbot_id(self, chatbot_id):
        return self.session.query(self.model). \
            filter(self.model.chatbot_id == chatbot_id).all()
    def get_by_metadatas(self, chatbot_id, metadatas):
        return self.session.query(self.model). \
            filter(self.model.chatbot_id == chatbot_id).filter(KnowledgeBase.metadatas == metadatas).all()
