from typing import Optional

from pydantic import BaseModel


class BaseEmbeddingCost(BaseModel):
    cost_usd: Optional[float] = None
    total_tokens: Optional[int] = None
    knowledgebase_id: Optional[int] = None

    class Config:
        orm_mode = True


class EmbeddingCostCreate(BaseEmbeddingCost):
    ...
