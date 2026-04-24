"""
User Schema Definitions
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
import re

# ============================================
# REQUEST DTOs (Input)
# ============================================


class UserRegisterRequest(BaseModel):
    """Register new user request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")
    name: str = Field(..., min_length=1, max_length=255, description="First name")
    surname: str = Field(..., min_length=1, max_length=255, description="Last name")
    phone: str = Field(..., description="Phone number (+393401234567)")
    role: str = Field(default="provider", description="User role: provider")

    # Optional fields
    city: str | None = Field(None, max_length=100, description="City")
    bio: str | None = Field(None, max_length=1000, description="Short bio")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate Italian phone format."""
        pattern = r"^\+39[0-9]{10}$"
        if not re.match(pattern, v):
            raise ValueError("Phone must be in format +393401234567")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate user role for registration."""
        if v != "provider":
            raise ValueError("Only 'provider' registration is allowed")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepass123",
                "name": "Arben",
                "surname": "Ahmeti",
                "phone": "+393401234567",
                "role": "provider",
                "city": "Tetovo",
            }
        }
    }


class UserLoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

    model_config = {"json_schema_extra": {"example": {"email": "user@example.com", "password": "securepass123"}}}


class UserProfileUpdateRequest(BaseModel):
    """Update user profile request."""

    name: str | None = Field(None, min_length=1, max_length=255)
    surname: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, description="Phone number")
    avatar_url: str | None = Field(None, max_length=500)
    bio: str | None = Field(None, max_length=1000)
    city: str | None = Field(None, max_length=100)
    address: str | None = Field(None, max_length=500)

    # Provider-specific
    years_of_experience: int | None = Field(None, ge=0, le=50)
    company_name: str | None = Field(None, max_length=255)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    fcm_token: str | None = Field(None, max_length=500)
    is_online: bool | None = Field(None)

    # Admin-only
    role: Literal["admin", "provider", "client"] | None = Field(None, description="User role")
    is_active: bool | None = Field(None)
    approval_status: str | None = Field(None, max_length=20)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Validate phone format if provided."""
        if v is None:
            return v
        pattern = r"^\+39[0-9]{10}$"
        if not re.match(pattern, v):
            raise ValueError("Phone must be in format +393401234567")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Arben",
                "surname": "Ahmeti",
                "phone": "+393405554440",
                "city": "Tetovo",
                "bio": "Usta me përvojë 10 vjeçare",
                "years_of_experience": 10,
                "latitude": 41.9981,
                "longitude": 21.4254,
            }
        }
    }


class UserLocationUpdateRequest(BaseModel):
    """Update the authenticated user's coordinates."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": 41.9981,
                "longitude": 21.4254,
            }
        }
    }


class PasswordChangeRequest(BaseModel):
    """Change password request."""

    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    model_config = {"json_schema_extra": {"example": {"old_password": "oldpass123", "new_password": "newpass123"}}}


# ============================================
# RESPONSE DTOs (Output)
# ============================================


class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    refresh_token: str | None = Field(None, description="Refresh token")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "refresh_token": "refresh_token_here",
            }
        }
    }


class UserProfileResponse(BaseModel):
    """User profile response."""

    id: UUID = Field(..., description="Profile ID")
    auth_user_id: UUID = Field(..., description="Authentication user ID")

    # Basic info
    name: str
    surname: str
    phone: str
    avatar_url: str | None = None
    bio: str | None = None

    # Role & status
    role: str

    # Location
    city: str | None = None
    address: str | None = None

    # Provider-specific
    years_of_experience: int | None = None
    company_name: str | None = None

    # Account/status
    is_active: bool
    is_online: bool
    approval_status: str
    latitude: float | None = None
    longitude: float | None = None
    fcm_token: str | None = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "auth_user_id": "987e6543-e21b-98d7-b654-321098765432",
                "name": "Arben",
                "surname": "Ahmeti",
                "phone": "+393401234567",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Usta me përvojë",
                "role": "provider",
                "city": "Tetovo",
                "address": None,
                "years_of_experience": 10,
                "company_name": "Ahmeti Construction",
                "is_active": True,
                "is_online": False,
                "approval_status": "approved",
                "latitude": 41.9981,
                "longitude": 21.4254,
                "fcm_token": "device-token",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "last_login": "2024-01-20T14:25:00Z",
            }
        },
    }


class UserPublicResponse(BaseModel):
    """Public user profile (limited info for listings)."""

    id: UUID
    name: str
    surname: str
    avatar_url: str | None = None
    role: str
    city: str | None = None
    years_of_experience: int | None = None

    # Stats (calculated)
    total_services: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Arben",
                "surname": "Ahmeti",
                "avatar_url": "https://example.com/avatar.jpg",
                "role": "provider",
                "city": "Tetovo",
                "years_of_experience": 10,
                "is_verified": True,
                "total_services": 5,
                "average_rating": 4.8,
                "total_reviews": 23,
            }
        },
    }


class UserListResponse(BaseModel):
    """Paginated user list response."""

    users: list[UserPublicResponse]
    total: int
    limit: int
    offset: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Arben",
                        "surname": "Ahmeti",
                        "role": "provider",
                        "city": "Tetovo",
                        "is_verified": True,
                        "total_services": 5,
                        "average_rating": 4.8,
                    }
                ],
                "total": 50,
                "limit": 20,
                "offset": 0,
            }
        }
    }


class AuthURLResponse(BaseModel):
    """OAuth authorization URL response."""

    auth_url: str = Field(..., description="Authorization URL")
    state: str | None = Field(None, description="CSRF state parameter")

    model_config = {
        "json_schema_extra": {
            "example": {
                "auth_url": "http://localhost:8001/authorize?client_id=...&redirect_uri=...",
                "state": "random_state_string",
            }
        }
    }


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")

    model_config = {"json_schema_extra": {"example": {"message": "Profile updated successfully", "success": True}}}


# ============================================
# QUERY PARAMETERS
# ============================================


class UserFilterParams(BaseModel):
    """User filtering and pagination parameters."""

    role: str | None = Field(None, description="Filter by role")
    city: str | None = Field(None, description="Filter by city")
    is_verified: bool | None = Field(None, description="Filter by verification status")
    search: str | None = Field(None, description="Search by name or company")

    # Pagination
    limit: int = Field(default=20, ge=1, le=100, description="Results per page")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")

    # Sorting
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order: asc or desc")

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order."""
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "provider",
                "city": "Tetovo",
                "is_verified": True,
                "search": "ahmeti",
                "limit": 20,
                "offset": 0,
                "sort_by": "created_at",
                "sort_order": "desc",
            }
        }
    }
