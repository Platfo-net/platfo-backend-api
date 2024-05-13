from sqlalchemy import String

from app.llms.models.knowledge_base import KnowledgeBase
from app.llms.repository.base_repository import CRUDBRepository


class KnowledgeBaseRepository(CRUDBRepository):
    model = KnowledgeBase

    def get_multi_by_chatbot_id(self, chatbot_id):
        return self.session.query(self.model). \
            filter(self.model.chatbot_id == chatbot_id).all()

    def get_by_metadata_values(self, chatbot_id, metadata_values):
        query = self.session.query(self.model).filter(self.model.chatbot_id == chatbot_id)
        for value in metadata_values:
            query = query.filter(self.model.metadatas.cast(String).ilike(f'%{value}%'))
        result = query.all()
        return result
