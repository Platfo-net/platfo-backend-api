from pydantic import BaseModel


class Image(BaseModel):
    filename: str = None
    url: str = None
