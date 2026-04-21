import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from workmate.domain.repositories.image_storage_port import IImageStoragePort
from workmate.domain.models.service_model import ServiceImage


class CloudinaryStorageAdapter(IImageStoragePort):
    """Cloudinary Implementation - Adapter që implementon IImageStoragePort"""

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """Initialize Cloudinary configuration"""
        cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)
        self._executor = ThreadPoolExecutor(max_workers=5)

    async def upload_image(
        self, file_path: str, folder: str, transformations: dict[str, Any] | None = None
    ) -> ServiceImage:
        """Upload single image në Cloudinary"""

        upload_options = {
            "folder": folder,
            "resource_type": "image",
            "quality": "auto:good",
            "fetch_format": "auto",
            "eager": [
                {"width": 800, "height": 600, "crop": "limit"},  # Main image
                {"width": 300, "height": 300, "crop": "fill"},  # Thumbnail
            ],
        }

        if transformations:
            upload_options.update(transformations)

        # Run blocking cloudinary call in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor, lambda: cloudinary.uploader.upload(file_path, **upload_options)
        )

        # Extract thumbnail URL from eager transformations
        thumbnail_url = None
        if "eager" in result and len(result["eager"]) > 1:
            thumbnail_url = result["eager"][1]["secure_url"]

        return ServiceImage(
            url=result["secure_url"],
            public_id=result["public_id"],
            width=result.get("width"),
            height=result.get("height"),
            format=result.get("format"),
            thumbnail_url=thumbnail_url,
        )

    async def upload_multiple_images(self, file_paths: list[str], folder: str) -> list[ServiceImage]:
        """Upload multiple images në Cloudinary - parallel"""

        tasks = [self.upload_image(file_path, folder) for file_path in file_paths]

        return await asyncio.gather(*tasks)

    async def delete_image(self, public_id: str) -> bool:
        """Delete single image nga Cloudinary"""

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self._executor, lambda: cloudinary.uploader.destroy(public_id))

        return result.get("result") == "ok"

    async def delete_multiple_images(self, public_ids: list[str]) -> bool:
        """Delete multiple images nga Cloudinary - parallel"""

        tasks = [self.delete_image(public_id) for public_id in public_ids]
        results = await asyncio.gather(*tasks)

        return all(results)

    def get_optimized_url(
        self, public_id: str, width: int | None = None, height: int | None = None, quality: str = "auto"
    ) -> str:
        """Generate optimized URL për image"""

        transformation = {"quality": quality, "fetch_format": "auto"}

        if width:
            transformation["width"] = width
        if height:
            transformation["height"] = height
            transformation["crop"] = "limit"

        return cloudinary.CloudinaryImage(public_id).build_url(**transformation)
