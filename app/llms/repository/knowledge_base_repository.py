import uuid

from sqlalchemy import or_

from app.llms.models.knowledge_base import KnowledgeBase
from app.llms.repository.base_repository import CRUDBRepository


class KnowledgeBaseRepository(CRUDBRepository):
    model = KnowledgeBase

    def get_multi_by_chatbot_id(self, chatbot_id):
        return self.session.query(self.model). \
            filter(self.model.chatbot_id == chatbot_id).all()

    def get_by_metadata_values(self, chatbot_id, metadata_values):
        uuid_objects = [uuid.UUID(u) for u in metadata_values]
        query = self.session.query(self.model).filter(self.model.chatbot_id == chatbot_id).filter(
            or_(self.model.uuid.in_(uuid_objects)))
        knowledge_base_objects = query.all()
        return knowledge_base_objects
