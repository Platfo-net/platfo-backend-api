from typing import Optional

from pydantic import BaseModel


class FileUpload(BaseModel):
    url: Optional[str] = None
    file_name: Optional[str] = None
