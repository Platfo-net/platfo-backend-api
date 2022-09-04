from typing import List, Optional
from pydantic import BaseModel, UUID4


class NodeUI(BaseModel):
    id: Optional[UUID4]
    text: Optional[str] = None
    width: Optional[int] = None
    heigth: Optional[int] = None
    data: Optional[dict]
    ports: List[dict]
    hasDeleteAction: Optional[bool] = None
    hasEditAction: Optional[bool] = None


class Edge(BaseModel):
    id: Optional[UUID4]
    from_id: Optional[UUID4]
    to_id: Optional[UUID4]
    fromPort: Optional[UUID4]
    toPort: Optional[UUID4]


class ChatflowUI(BaseModel):

    nodes: List[NodeUI]
    edges: List[Edge]
