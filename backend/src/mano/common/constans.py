"""
Application Constants - Centralized constant values
Domain Layer - Business rules and configuration
"""


# ============================================
# HTTP Status Codes
# ============================================
class HTTPStatus:
    """HTTP status code constants."""

    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # Server Errors
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503


# ============================================
# Database Field Lengths
# ============================================
class FieldLength:
    """Database field length constants."""

    # User fields
    EMAIL = 255
    NAME = 255
    PHONE = 20
    CITY = 100
    ADDRESS = 500
    BIO = 1000

    # Service fields
    TITLE = 255
    DESCRIPTION = 5000
    SHORT_DESCRIPTION = 500
    UUID_STRING = 36
    # Review fields
    COMMENT = 2000

    # Category fields
    CATEGORY_NAME = 100
    CATEGORY_SLUG = 100
    ICON = 50

    # General
    UUID_STRING = 36
    CURRENCY = 3
    ROLE = 20
    STATUS = 20
    ENUM_VALUE = 50
    TIME = 5  # "HH:MM"
    URL = 500


# ============================================
# Pagination Defaults
# ============================================
class Pagination:
    """Pagination constants."""

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100
    MIN_LIMIT = 1
    DEFAULT_OFFSET = 0

    # Specific use cases
    SEARCH_RESULTS_LIMIT = 50
    MESSAGES_LIMIT = 50
    NOTIFICATIONS_LIMIT = 30
    REVIEWS_LIMIT = 20
    BOOKINGS_LIMIT = 20


# ============================================
# Database Configuration
# ============================================
class DatabaseDefaults:
    """Database configuration constants."""

    POSTGRES_PORT = 5432
    REDIS_PORT = 6379

    # Connection pool
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600

    # Query timeout
    STATEMENT_TIMEOUT = 30000  # 30 seconds in milliseconds
