"""Endpoint for backup related processes."""

from fastapi import APIRouter, status
from backbone.code.backup import (
    backup_crops,
    backup_images,
    backup_labels,
    get_new_version_id,
)

router = APIRouter()


@router.post(
    "/backup",
    status_code=status.HTTP_201_CREATED,
)
def backup_data():
    """Backup processed data.
    Useful for when DBD releases a new endcard style.
    """
    version_id = get_new_version_id()
    backup_crops(version_id)
    backup_images(version_id)
    backup_labels(version_id)
