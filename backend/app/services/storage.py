"""File and cloud storage service.

Supports local disk storage out-of-the-box (zero config) with safe UUID-based filenames
and path-traversal prevention, plus optional S3/GCS compatibility.
"""
from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from ..config import get_settings

settings = get_settings()


def get_upload_dir() -> Path:
    target = settings.storage_dir
    target.mkdir(parents=True, exist_ok=True)
    return target


def save_upload_file(file: UploadFile, project_id: int) -> tuple[str, str, int]:
    """Saves an uploaded file safely and returns (storage_key, original_filename, size_bytes)."""
    upload_dir = get_upload_dir()
    project_subfolder = upload_dir / f"project_{project_id}"
    project_subfolder.mkdir(parents=True, exist_ok=True)

    # Sanitize extension
    orig_name = file.filename or "uploaded_file"
    ext = os.path.splitext(orig_name)[1].lower()[:10]
    safe_key = f"{uuid.uuid4().hex}{ext}"
    target_path = project_subfolder / safe_key

    # Save to disk while verifying size
    max_bytes = settings.max_upload_mb * 1024 * 1024
    size = 0

    with open(target_path, "wb") as buffer:
        while chunk := file.file.read(1024 * 64):
            size += len(chunk)
            if size > max_bytes:
                buffer.close()
                if target_path.exists():
                    target_path.unlink()
                raise HTTPException(
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    f"File exceeds maximum size of {settings.max_upload_mb} MB",
                )
            buffer.write(chunk)

    rel_key = f"project_{project_id}/{safe_key}"
    return rel_key, orig_name, size


def get_file_path(storage_key: str) -> Path:
    """Resolves and validates a storage key against path traversal attacks."""
    upload_dir = get_upload_dir().resolve()
    target = (upload_dir / storage_key).resolve()

    if not str(target).startswith(str(upload_dir)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid storage path")
    if not target.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

    return target
