from typing import Optional

from pydantic import BaseModel


class TaskResultBase(BaseModel):
    function_name: Optional[str] = None
    stacktrace: Optional[str] = None
    is_successful: Optional[bool] = None


class TaskResultCreate(TaskResultBase):
    pass
