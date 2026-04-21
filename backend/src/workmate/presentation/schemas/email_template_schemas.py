"""Email template schemas."""

from __future__ import annotations


from pydantic import BaseModel, Field, ConfigDict


class EmailTemplateBase(BaseModel):
    """Base email template schema."""

    name: str = Field(..., description="Template name")
    subject: str = Field(..., description="Email subject")
    html_content: str = Field(..., description="HTML content")
    text_content: str | None = Field(None, description="Plain text content")
    is_active: bool = Field(True, description="Whether template is active")


class EmailTemplateCreate(EmailTemplateBase):
    """Schema for creating email template."""

    pass


class EmailTemplateUpdate(BaseModel):
    """Schema for updating email template."""

    name: str | None = Field(None, description="Template name")
    subject: str | None = Field(None, description="Email subject")
    html_content: str | None = Field(None, description="HTML content")
    text_content: str | None = Field(None, description="Plain text content")
    is_active: bool | None = Field(None, description="Whether template is active")


class EmailTemplateResponse(EmailTemplateBase):
    """Schema for email template response."""

    id: str = Field(..., description="Template ID")

    model_config = ConfigDict(from_attributes=True)


class EmailTemplateListResponse(BaseModel):
    """Schema for email template list response."""

    templates: list[EmailTemplateResponse] = Field(..., description="List of email templates")
    total: int = Field(..., description="Total number of templates")
