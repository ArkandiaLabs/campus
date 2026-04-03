from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProgressCreate(BaseModel):
    content_id: UUID


class ProgressRecord(BaseModel):
    id: UUID
    user_id: UUID
    content_id: UUID
    completed_at: datetime
