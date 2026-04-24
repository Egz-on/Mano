"""Job API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateJobSchema(BaseModel):
    """Request payload for creating a job."""

    customer_id: UUID
    category_id: UUID
    description: str = Field(..., min_length=10)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str = Field(..., min_length=3, max_length=500)
    photo_urls: list[str] = Field(default_factory=list)


class UpdateJobSchema(BaseModel):
    """Request payload for updating a job."""

    category_id: UUID | None = None
    description: str | None = Field(default=None, min_length=10)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    address: str | None = Field(default=None, min_length=3, max_length=500)
    photo_urls: list[str] | None = None


class AssignTechnicianSchema(BaseModel):
    """Request payload for assigning a technician."""

    technician_id: UUID


class SubmitQuoteSchema(BaseModel):
    """Request payload for quote submission."""

    amount: str = Field(..., min_length=1, max_length=20)
    description: str = Field(..., min_length=3)


class UpdateJobStatusSchema(BaseModel):
    """Request payload for changing job status."""

    status: Literal["assigned", "en_route", "arrived", "diagnosed", "in_progress", "completed", "cancelled"]


class JobResponseSchema(BaseModel):
    """Response payload for jobs."""

    id: UUID
    customer_id: UUID
    technician_id: UUID | None
    category_id: UUID
    description: str
    photo_urls: list[str]
    latitude: float
    longitude: float
    address: str
    status: str
    call_out_fee_paid: bool
    chat_unlocked: bool
    quote_amount: str | None
    quote_description: str | None
    quote_submitted_at: datetime | None
    quote_approved_at: datetime | None
    quote_rejected_at: datetime | None
    created_at: datetime
    updated_at: datetime
