"""Schemas for local authentication endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=128)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)
    surname: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=12, max_length=20, description="Phone in +389XXXXXXXX format")
    role: Literal["client", "provider"] = "client"
    city: str | None = Field(default=None, max_length=100)
    company_name: str | None = Field(default=None, max_length=255)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=16, max_length=512)
    new_password: str = Field(..., min_length=8, max_length=128)


class AuthUserResponse(BaseModel):
    email: EmailStr
    name: str
    surname: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserResponse


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str | None = Field(default=None, description="Only present in development mode")


class MessageResponse(BaseModel):
    message: str
