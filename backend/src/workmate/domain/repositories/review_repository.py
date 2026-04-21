from __future__ import annotations
from abc import ABC, abstractmethod
from workmate.domain.models.review import Review, ReviewId
from workmate.domain.models.service_model import ServiceId


class ReviewRepository(ABC):
    """Abstract base class for Service repository."""

    @abstractmethod
    async def add_review(self, review: Review) -> Review:
        """Create a new review"""
        ...

    @abstractmethod
    async def get_by_id(self, review_id: ReviewId) -> Review | None:
        """Get review by ID."""
        ...

    @abstractmethod
    async def list_by_service(self, service_id: ServiceId) -> list[Review]:
        """List reviews for a service."""
        ...

    @abstractmethod
    async def update(self, review: Review) -> Review:
        """Update a review."""
        ...

    @abstractmethod
    async def delete(self, review_id: ReviewId) -> None:
        """Delete a review."""
        ...
