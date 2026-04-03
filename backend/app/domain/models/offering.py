from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class UserOffering(BaseModel):
    id: UUID
    title: str
    description: str | None
    type: str
    status: str
    cohort_title: str | None
    start_date: date | None
    end_date: date | None
    purchased_at: datetime
    total_contents: int
    completed_contents: int


class ContentItem(BaseModel):
    id: UUID
    title: str
    description: str | None
    content_type: Literal["video", "download", "link"]
    content_url: str
    position: int
    is_preview: bool
    completed: bool


class OfferingDetail(BaseModel):
    id: UUID
    title: str
    description: str | None
    cohort_title: str | None
    start_date: date | None
    end_date: date | None
    contents: list[ContentItem]
    total_contents: int
    completed_contents: int
