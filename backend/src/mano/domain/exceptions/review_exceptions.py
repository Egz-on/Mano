"""Review domain exceptions."""

from mano.domain.exceptions.base import DomainError


class ReviewNotFound(DomainError):
    """Review not found exception."""

    pass


class ReviewValidationError(DomainError):
    """Review validation error exception."""

    pass
