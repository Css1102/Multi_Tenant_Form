from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from app.worker.tasks import generate_csv_export
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from ..dependencies import get_current_user
router = APIRouter(prefix="/exports", tags=["Exports"])

EXPORT_DIR = "secure_exports"

@router.get("/download/{filename}")
def download_export(filename: str, current_user = Depends(get_current_user)):
    """
    Securely serves the generated CSV file back to the client.
    """
    # Security check: Ensure the user is only downloading their own tenant's files
    # Our filename format is "export_{tenant_id}_{form_id}.csv"
    if str(current_user.organization_id) not in filename:
        raise HTTPException(status_code=403, detail="Unauthorized to access this file")
        
    file_path = os.path.join(EXPORT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or expired")
        
    # FileResponse forces the browser to download the file rather than trying to display it
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type="text/csv"
    )