from abc import ABC, abstractmethod
from typing import Any
from workmate.domain.models.service_model import ServiceImage


class IImageStoragePort(ABC):
    """Port për Image Storage - Cloudinary interface"""

    @abstractmethod
    async def upload_image(
        self, file_path: str, folder: str, transformations: dict[str, Any] | None = None
    ) -> ServiceImage:
        """Upload single image"""
        ...

    @abstractmethod
    async def upload_multiple_images(self, file_paths: list[str], folder: str) -> list[ServiceImage]:
        """Upload multiple images"""
        ...

    @abstractmethod
    async def delete_image(self, public_id: str) -> bool:
        """Delete image"""
        ...

    @abstractmethod
    async def delete_multiple_images(self, public_ids: list[str]) -> bool:
        """Delete multiple images"""
        ...

    @abstractmethod
    def get_optimized_url(
        self, public_id: str, width: int | None = None, height: int | None = None, quality: str = "auto"
    ) -> str:
        """Get optimized image URL"""
        ...
