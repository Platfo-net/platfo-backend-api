import datetime

from sqlalchemy import (Boolean, Column, DateTime,
                        String, Text)

from app.db.base_class import Base


class TaskResult(Base):
    __tablename__ = 'task_results'

    function_name = Column(String(255), nullable=True)
    stacktrace = Column(Text(), nullable=True)
    is_successful = Column(Boolean())
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
