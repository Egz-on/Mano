from pydantic import BaseModel, EmailStr, Field, model_validator
from uuid import UUID
from datetime import datetime


class ReviewCreateSchema(BaseModel):
    client_id: UUID | None = Field(None, description="Optional ID of the client creating the review")
    provider_id: UUID = Field(..., description="ID of the provider of the service")
    service_id: UUID = Field(..., description="ID of the service being reviewed")
    rating: int = Field(..., description="Rating given by the user")
    comment: str | None = Field(None, description="Optional comment for the review")
    guest_name: str | None = Field(None, description="Guest name when client_id is not provided")
    guest_email: EmailStr | None = Field(None, description="Guest email when client_id is not provided")

    @model_validator(mode="after")
    def validate_guest_identity(self) -> "ReviewCreateSchema":
        if self.client_id is None and (not self.guest_name or not self.guest_email):
            raise ValueError("Guest reviews require both guest_name and guest_email")
        return self


class ReviewResponseSchema(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the review")
    user_id: UUID = Field(..., description="ID of the user who created the review")
    client_id: UUID = Field(..., description="ID of the client receiving the review")
    provider_id: UUID = Field(..., description="ID of the provider of the service")
    service_id: UUID = Field(..., description="ID of the service being reviewed")
    rating: int = Field(..., description="Rating given by the user")
    comment: str | None = Field(None, description="Optional comment for the review")
    guest_name: str | None = Field(None, description="Guest reviewer name if anonymous review")
    guest_email: EmailStr | None = Field(None, description="Guest reviewer email if anonymous review")
    status: str = Field(..., description="Status of the review")
    moderated_by: UUID | None = Field(None, description="ID of the moderator")
    moderation_notes: str | None = Field(None, description="Notes from the moderator")
    created_at: datetime = Field(..., description="Timestamp when the review was created")
    updated_at: datetime = Field(..., description="Timestamp when the review was last updated")


class ReviewUpdateSchema(BaseModel):
    rating: int | None = Field(None, description="New rating")
    comment: str | None = Field(None, description="New comment")
