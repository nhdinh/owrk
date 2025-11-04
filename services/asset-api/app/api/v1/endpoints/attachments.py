"""
Attachment API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from app.core.dependencies import get_current_user
from app.models.attachment import FileType
from app.schemas.asset_schema import AttachmentResponse
from app.services.file_service import FileService

router = APIRouter()


@router.post(
    "/{asset_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    asset_id: int,
    file: UploadFile = File(...),
    file_type: FileType = Form(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload file attachment for asset"""
    try:
        attachment = await FileService.upload_attachment(
            asset_id=asset_id,
            file=file,
            file_type=file_type,
            uploaded_by=current_user["sub"],
        )
        return attachment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{asset_id}/attachments", response_model=List[AttachmentResponse])
async def list_attachments(
    asset_id: int, current_user: dict = Depends(get_current_user)
):
    """List all attachments for an asset"""
    try:
        attachments = await FileService.get_asset_attachments(asset_id)
        return attachments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: int, current_user: dict = Depends(get_current_user)
):
    """Delete attachment"""
    try:
        await FileService.delete_attachment(attachment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
