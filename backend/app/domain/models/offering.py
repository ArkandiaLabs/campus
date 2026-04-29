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


class ContentItem(BaseModel):
    id: UUID
    title: str
    description: str | None
    content_type: Literal["video", "download", "link"]
    content_url: str
    position: int
    is_preview: bool


class SessionSummary(BaseModel):
    id: UUID
    title: str
    scheduled_at: datetime | None
    duration_minutes: int | None


class SessionDetail(BaseModel):
    id: UUID
    title: str
    description: str | None
    scheduled_at: datetime | None
    duration_minutes: int | None
    contents: list[ContentItem]


class OfferingDetail(BaseModel):
    id: UUID
    title: str
    description: str | None
    cohort_title: str | None
    start_date: date | None
    end_date: date | None
    sessions: list[SessionSummary]
    general_resources: list[ContentItem]
