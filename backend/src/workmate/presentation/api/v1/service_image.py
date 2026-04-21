from fastapi import APIRouter, UploadFile, File, Depends
from typing import Any
from uuid import UUID
from workmate.dependencies import get_service_service
from workmate.domain.services.service_services import ServiceService

router = APIRouter(prefix="/{service_id}/images", tags=["Service Images"])


@router.post("/upload")
async def upload_service_images(
    service_id: UUID,
    files: list[UploadFile] = File(...),
    service_service: ServiceService = Depends(get_service_service),
) -> dict[str, Any]:
    """Upload images for a service"""
    import tempfile
    import os

    # Save uploaded files temporarily
    file_paths = []
    for file in files:
        suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            content = await file.read()
            f.write(content)
            file_paths.append(f.name)

    # Upload to Cloudinary
    images = await service_service.upload_service_images(service_id, file_paths)

    # Clean up temp files
    import os

    for path in file_paths:
        os.remove(path)

    return {
        "success": True,
        "images": [{"url": img.url, "public_id": img.public_id, "thumbnail_url": img.thumbnail_url} for img in images],
    }


@router.delete("/")
async def delete_service_images(
    service_id: UUID, public_ids: list[str], service_service: ServiceService = Depends(get_service_service)
) -> dict[str, bool]:
    """Delete images for a service"""
    success = await service_service.delete_service_images(public_ids)

    return {"success": success}
