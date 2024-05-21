from chromadb import ClientAPI

from app.core.config import settings
from app.core.storage import get_object_url
from app.llms.models import ChatBot
from app.llms.repository.knowledge_base_repository import KnowledgeBaseRepository
from app.llms.services.base_service import BaseService


class KnowledgeBaseService(BaseService):

    def __init__(self, knowledge_base_repo: KnowledgeBaseRepository):
        self.knowledge_base_repo = knowledge_base_repo
        super().__init__(knowledge_base_repo)

    def get_multi_by_chatbot_id(self, chatbot_id, current_user):
        chatbot = self.validator.validate_generic_exists(uuid=chatbot_id, model=ChatBot)
        self.validator.validate_user_ownership(obj=chatbot, current_user=current_user)

        knowledge_bases = self.knowledge_base_repo.get_multi_by_chatbot_id(chatbot_id=chatbot.id)
        modified_knowledge_bases = []
        for kb in knowledge_bases:
            kb.chatbot_id = chatbot.uuid
            kb.file_url = get_object_url(kb.file_path, settings.S3_KNOWLEDGE_BASE_BUCKET)
            modified_knowledge_bases.append(kb)
        return modified_knowledge_bases

    def get_by_metadata_values(self, chatbot_id, metadata_values):
        if metadata_values:
            return self.knowledge_base_repo.get_by_metadata_values(chatbot_id=chatbot_id,
                                                                   metadata_values=metadata_values)
        return []

    def create(self, schema, current_user):
        chatbot = self.validator.validate_generic_exists(uuid=schema.chatbot_id, model=ChatBot)
        self.validator.validate_user_ownership(obj=chatbot, current_user=current_user)

        schema.chatbot_id = chatbot.id

        new_knowledge_base = self.knowledge_base_repo.create(schema)
        new_knowledge_base.chatbot_id = chatbot.uuid
        return new_knowledge_base

    def remove_with_embeddings(self, db_obj, chroma: ClientAPI):
        chroma.get_collection(name=str(db_obj.chatbot.uuid)).delete(
            where={"unique_identifier": str(db_obj.uuid)})
        return self.knowledge_base_repo.delete(db_obj.id)
