from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = 1
    total_pages: int = 1
    page_size: int = 20
    total_count: int = 20
