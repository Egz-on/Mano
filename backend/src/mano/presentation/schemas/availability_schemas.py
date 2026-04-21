"""
Availability Schema Definitions
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateAvailabilitySchema(BaseModel):
    """Schema for creating a new availability slot."""

    provider_id: UUID = Field(..., description="Provider ID")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Mon, 6=Sun)")
    start_time: str = Field(..., description="Start time in HH:MM")
    end_time: str = Field(..., description="End time in HH:MM")
    is_available: bool = Field(default=True, description="Whether provider is available")
    specific_date: datetime | None = Field(None, description="Specific date override")

    model_config = {
        "json_schema_extra": {
            "example": {
                "provider_id": "123e4567-e89b-12d3-a456-426614174000",
                "day_of_week": 1,
                "start_time": "09:00",
                "end_time": "17:00",
                "is_available": True,
                "specific_date": None,
            }
        }
    }


class UpdateAvailabilitySchema(BaseModel):
    """Schema for updating an availability slot."""

    day_of_week: int | None = Field(None, ge=0, le=6, description="Day of week (0=Mon, 6=Sun)")
    start_time: str | None = Field(None, description="Start time in HH:MM")
    end_time: str | None = Field(None, description="End time in HH:MM")
    is_available: bool | None = Field(None, description="Whether provider is available")
    specific_date: datetime | None = Field(None, description="Specific date override")

    model_config = {
        "json_schema_extra": {
            "example": {
                "day_of_week": 2,
                "start_time": "10:00",
                "end_time": "18:00",
                "is_available": False,
                "specific_date": None,
            }
        }
    }


class AvailabilityResponseSchema(BaseModel):
    """Schema for availability response."""

    id: UUID = Field(..., description="Availability ID")
    provider_id: UUID = Field(..., description="Provider ID")
    day_of_week: int = Field(..., description="Day of week (0=Mon, 6=Sun)")
    start_time: str = Field(..., description="Start time in HH:MM")
    end_time: str = Field(..., description="End time in HH:MM")
    is_available: bool = Field(..., description="Whether provider is available")
    specific_date: datetime | None = Field(None, description="Specific date override")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174010",
                "provider_id": "123e4567-e89b-12d3-a456-426614174000",
                "day_of_week": 1,
                "start_time": "09:00",
                "end_time": "17:00",
                "is_available": True,
                "specific_date": None,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-10T12:00:00Z",
            }
        }
    }
