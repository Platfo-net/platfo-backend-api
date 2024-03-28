from app.llms.models import ChatBot
from app.llms.repository.knowledge_base_repository import KnowledgeBaseRepository
from app.llms.services.base_service import BaseService


class KnowledgeBaseService(BaseService):

    def __init__(self, knowledge_base_repo: KnowledgeBaseRepository):
        self.knowledge_base_repo = knowledge_base_repo
        super().__init__(knowledge_base_repo)

    def get_list_by_chatbot_id(self, chatbot_id, current_user):
        chatbot = self.validator.validate_generic_exists(uuid=chatbot_id,
                                                         model=ChatBot)
        self.validator.validate_user_ownership(obj=chatbot, current_user=current_user)
        knowledge_bases = self.knowledge_base_repo.get_multi_by_chatbot_id(chatbot_id=chatbot.id)
        modified_knowledge_bases = []
        for kb in knowledge_bases:
            kb.chatbot_id = chatbot.uuid
            modified_knowledge_bases.append(kb)
        return modified_knowledge_bases

    def add(self, schema):
        chatbot = self.validator.validate_generic_exists(uuid=schema.chatbot_id,
                                                         model=ChatBot)
        schema.chatbot_id = chatbot.id
        new_knowledge_base = self.knowledge_base_repo.create(schema)

        new_knowledge_base.chatbot_id = chatbot.uuid
        return new_knowledge_base
