from enum import Enum
from typing import Optional

from pydantic import BaseModel, UUID4
from pydantic import HttpUrl

from app.llms.schemas.base_schema import ModelBaseInfo


class KnowledgeBaseType(str, Enum):
    PDF = "pdf"
    TXT = "txt"


class BaseKnowledgeBase(BaseModel):
    name: str
    metadatas: Optional[dict] = None
    type: Optional[KnowledgeBaseType] = KnowledgeBaseType.PDF
    file_path: Optional[HttpUrl] = None
    chatbot_id: Optional[UUID4] = None

    class Config:
        orm_mode = True


class KnowledgeBaseCreate(BaseKnowledgeBase):
    ...


class KnowledgeBaseUpdate(BaseKnowledgeBase):
    ...


class KnowledgeBase(ModelBaseInfo, BaseKnowledgeBase):
    ...
