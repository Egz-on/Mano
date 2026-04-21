from typing import Literal, TypeVar

from fastapi import HTTPException, Query, status
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parameters for pagination, sorting, and ordering."""

    page: int = Field(1, ge=1, description="Page number (1-based)")
    limit: int = Field(10, ge=1, le=100, description="Items per page")
    sort: str | None = Field(None, description="Sort field")
    order: Literal["asc", "desc"] = Field("desc", description="Sort order")

    @classmethod
    def from_query(
        cls,
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        limit: int = Query(10, ge=1, le=100, description="Items per page"),
        sort: str | None = Query(None, description="Sort field"),
        order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
    ) -> "PaginationParams":
        return cls(page=page, limit=limit, sort=sort, order=order)


class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""

    page: int
    limit: int
    total_items: int
    total_pages: int
    sort: str | None
    order: str


class PaginatedResponse[T](BaseModel):
    """Generic paginated response model."""

    items: list[T]
    meta: PaginationMeta


class Pagination:
    @staticmethod
    def paginate_items(items: list[T], params: PaginationParams) -> PaginatedResponse[T]:
        """Paginate a list of items based on the given pagination parameters."""
        total_items = len(items)
        total_pages = (total_items + params.limit - 1) // params.limit if params.limit else 1
        if params.page > total_pages and total_items > 0:
            raise Pagination.pagination_exception(f"Page {params.page} out of range. Max page is {total_pages}")
        start = (params.page - 1) * params.limit
        end = start + params.limit
        paged_items = items[start:end]
        meta = PaginationMeta(
            page=params.page,
            limit=params.limit,
            total_items=total_items,
            total_pages=total_pages,
            sort=params.sort,
            order=params.order,
        )
        return PaginatedResponse(items=paged_items, meta=meta)

    @staticmethod
    def pagination_exception(detail: str) -> HTTPException:
        """Create an HTTPException for pagination errors."""
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "pagination_error",
                "message": detail,
            },
        )
