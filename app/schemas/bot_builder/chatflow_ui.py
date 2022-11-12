from typing import List, Optional
from pydantic import BaseModel, UUID4


class NodeUI(BaseModel):
    id: Optional[UUID4]
    text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    data: Optional[dict] = None
    ports: List[dict]
    has_delete_action: Optional[bool] = None
    has_edit_action: Optional[bool] = None


class Edge(BaseModel):
    id: Optional[UUID4]
    from_id: Optional[UUID4]
    to_id: Optional[UUID4]
    from_port: Optional[UUID4]
    to_port: Optional[UUID4]
    from_widget: Optional[UUID4]
    text: Optional[str] = None


class ChatflowUI(BaseModel):
    name: Optional[str] = None
    chatflow_id: Optional[UUID4] = None
    nodes: List[NodeUI]
    edges: List[Edge]
