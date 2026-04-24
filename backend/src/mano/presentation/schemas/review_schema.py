from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ReviewCreateSchema(BaseModel):
    client_id: UUID = Field(..., description="ID of the client creating the review")
    provider_id: UUID = Field(..., description="ID of the provider of the service")
    service_id: UUID = Field(..., description="ID of the service being reviewed")
    rating: int = Field(..., description="Rating given by the user")
    comment: str | None = Field(None, description="Optional comment for the review")


class ReviewResponseSchema(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the review")
    user_id: UUID = Field(..., description="ID of the user who created the review")
    client_id: UUID = Field(..., description="ID of the client receiving the review")
    provider_id: UUID = Field(..., description="ID of the provider of the service")
    service_id: UUID = Field(..., description="ID of the service being reviewed")
    rating: int = Field(..., description="Rating given by the user")
    comment: str | None = Field(None, description="Optional comment for the review")
    status: str = Field(..., description="Status of the review")
    moderated_by: UUID | None = Field(None, description="ID of the moderator")
    moderation_notes: str | None = Field(None, description="Notes from the moderator")
    created_at: datetime = Field(..., description="Timestamp when the review was created")
    updated_at: datetime = Field(..., description="Timestamp when the review was last updated")


class ReviewUpdateSchema(BaseModel):
    rating: int | None = Field(None, description="New rating")
    comment: str | None = Field(None, description="New comment")
