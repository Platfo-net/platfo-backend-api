from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel

from app.llms.schemas.base_schema import ModelBaseInfo


class KnowledgeBaseType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    CRAWLER = "crawler"


class BaseKnowledgeBase(BaseModel):
    name: str
    metadatas: Optional[dict] = None
    type: Optional[KnowledgeBaseType] = KnowledgeBaseType.PDF
    file_path: Optional[str] = None
    urls: Optional[List[str]] = None
    source_link: Optional[str] = None
    chatbot_id: Optional[UUID4] = None

    class Config:
        orm_mode = True


class KnowledgeBaseCreate(BaseKnowledgeBase):
    ...


class KnowledgeBaseUpdate(BaseKnowledgeBase):
    ...


class KnowledgeBase(ModelBaseInfo, BaseKnowledgeBase):
    file_url: Optional[str] = None
