"""
File Service - Handle file uploads
"""

import os
import logging
from typing import Optional
from pathlib import Path
import aiofiles
from fastapi import UploadFile

from app.core.config import settings
from app.core.unit_of_work import UnitOfWork
from app.models.attachment import AssetAttachment, FileType

logger = logging.getLogger(__name__)


class FileService:
    """Service for file upload and management"""

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename"""
        return Path(filename).suffix.lower()

    @staticmethod
    def validate_file(filename: str, file_size: int) -> tuple[bool, Optional[str]]:
        """
        Validate file extension and size

        Args:
            filename: Original filename
            file_size: File size in bytes

        Returns:
            (is_valid, error_message)
        """
        # Check file extension
        ext = FileService.get_file_extension(filename)
        if ext not in settings.ALLOWED_EXTENSIONS:
            return (
                False,
                f"File type {ext} not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}",
            )

        # Check file size
        if file_size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            return False, f"File size exceeds maximum allowed size of {max_mb}MB"

        return True, None

    @staticmethod
    async def save_file(file: UploadFile, asset_id: int, file_type: FileType) -> str:
        """
        Save uploaded file to disk

        Args:
            file: Uploaded file
            asset_id: Asset ID
            file_type: Type of file

        Returns:
            File path

        Raises:
            ValueError: If file validation fails
        """
        # Validate file
        content = await file.read()
        file_size = len(content)
        is_valid, error = FileService.validate_file(file.filename, file_size)
        if not is_valid:
            raise ValueError(error)

        # Reset file pointer
        await file.seek(0)

        # Create directory structure
        asset_dir = Path(settings.UPLOAD_DIR) / str(asset_id) / file_type.value.lower()
        asset_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        import uuid

        ext = FileService.get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = asset_dir / unique_filename

        # Save file
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        logger.info(f"File saved: {file_path}")

        # Return relative path
        return str(file_path.relative_to(settings.UPLOAD_DIR))

    @staticmethod
    async def upload_attachment(
        asset_id: int, file: UploadFile, file_type: FileType, uploaded_by: int
    ) -> AssetAttachment:
        """
        Upload file attachment for asset

        Args:
            asset_id: Asset ID
            file: Uploaded file
            file_type: Type of file
            uploaded_by: User ID who uploaded

        Returns:
            Created attachment record

        Raises:
            ValueError: If validation fails
        """
        with UnitOfWork() as uow:
            # Check if asset exists
            asset = uow.assets.get_by_id(asset_id)
            if not asset or asset.deleted_at:
                raise ValueError("Asset not found")

            # Save file
            file_path = await FileService.save_file(file, asset_id, file_type)

            # Create attachment record
            content = await file.read()
            attachment = AssetAttachment(
                asset_id=asset_id,
                file_name=file.filename,
                file_type=file_type,
                file_url=file_path,
                file_size=len(content),
                uploaded_by=uploaded_by,
            )

            attachment = uow.attachments.create(attachment)
            uow.commit()

            logger.info(f"Attachment created for asset {asset_id}: {file.filename}")
            return attachment

    @staticmethod
    async def delete_attachment(attachment_id: int) -> bool:
        """
        Delete attachment

        Args:
            attachment_id: Attachment ID

        Returns:
            True if successful

        Raises:
            ValueError: If attachment not found
        """
        with UnitOfWork() as uow:
            attachment = uow.attachments.get_by_id(attachment_id)
            if not attachment:
                raise ValueError("Attachment not found")

            # Delete file from disk
            file_path = Path(settings.UPLOAD_DIR) / attachment.file_url
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")

            # Delete record
            uow.attachments.delete(attachment_id)
            uow.commit()

            return True

    @staticmethod
    async def get_asset_attachments(asset_id: int):
        """Get all attachments for an asset"""
        with UnitOfWork() as uow:
            return uow.attachments.get_asset_attachments(asset_id)
