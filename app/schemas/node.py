from typing import List, Optional

from .chatflow import Chatflow
from pydantic import UUID4, BaseModel


class QuickReply(BaseModel):
    id: UUID4
    text: Optional[str] = None


class NodeBase(BaseModel):
    title: Optional[str] = None
    chatflow_id: Optional[UUID4] = None
    from_widget: List[UUID4] = None
    widget: dict = None
    quick_replies: Optional[List[QuickReply]] = None


class NodeCreate(BaseModel):
    title: Optional[str] = None
    chatflow_id: UUID4
    is_head: Optional[bool] = False
    quick_replies: Optional[List[QuickReply]] = None


class FullNodeCreate(BaseModel):
    title: Optional[str] = None
    chatflow_id: UUID4
    widget: dict = None
    widget_type: str = None
    is_head: Optional[bool] = False
    quick_replies: List[QuickReply]


class NodeUpdate(BaseModel):
    title: Optional[str] = None
    chatflow_id: Optional[UUID4] = None


class Node(NodeBase):
    id: UUID4
    chatflow: Optional[Chatflow]
    is_head: Optional[bool] = False

    class Config:
        orm_mode = True


class MessageWidgetCreate(BaseModel):
    message: Optional[str] = None


class MenuWidgetChoices(BaseModel):
    text: Optional[str] = None


class MenuWidgetCreate(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None
    choices: List[MenuWidgetChoices]


class QuickReply(BaseModel):
    title: Optional[str] = None


class MediaWidget(BaseModel):
    file_id: Optional[str] = None
