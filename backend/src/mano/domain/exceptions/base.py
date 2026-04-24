"""Base domain exceptions."""


class DomainError(Exception):
    """Base domain exception."""


class UserNotFoundError(DomainError):
    """User not found exception."""


class ServiceNotFoundError(DomainError):
    """Service not found exception."""


class ServiceAlreadyExistsError(DomainError):
    """Service already exists exception."""


class AvailabilityNotFoundError(DomainError):
    """Availability not found exception."""


class CategoryNotFoundError(DomainError):
    """Category not found exception."""


class CategoryAlreadyExistsError(DomainError):
    """Category already exists exception."""


class EmailAlreadyRegisteredError(DomainError):
    """Email already exists in the local auth system."""


class InvalidPasswordResetTokenError(DomainError):
    """Password reset token is invalid or expired."""


class EmailDeliveryError(DomainError):
    """Email could not be delivered."""


class PermissionError(DomainError):
    """Permission denied exception."""


class JobNotFoundError(DomainError):
    """Job not found exception."""


class JobStateError(DomainError):
    """Invalid job lifecycle operation."""
