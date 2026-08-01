import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from uuid import UUID, uuid4
from ..database import get_session
from ..models import FileAttachment, User
from ..dependencies import get_current_user

router = APIRouter(prefix="/files", tags=["Files"])

# In production, this would be an S3 bucket path.
UPLOAD_DIR = "secure_storage_vault/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_MIME_TYPES = ["application/pdf", "image/jpeg", "image/png"]
MAX_FILE_SIZE_MB = 10

@router.post("/upload/{submission_id}")
async def upload_attachment(
    submission_id: UUID,
    # UploadFile automatically handles the multipart/form-data parsing
    file: UploadFile = File(...), 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Immediate Security Validations
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported file type.")
    
    # 2. Obfuscate the filename to prevent directory traversal attacks
    secure_filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, secure_filename)
    
    total_size = 0
    
    # 3. Stream the file directly to disk asynchronously using 'aiofiles'
    # This prevents the server from freezing while waiting for disk I/O
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(1024 * 1024): # Read in 1MB chunks
                total_size += len(chunk)
                
                # Check file size limit during the stream
                if total_size > (MAX_FILE_SIZE_MB * 1024 * 1024):
                    raise HTTPException(status_code=413, detail="File exceeds 10MB limit.")
                    
                await out_file.write(chunk)
    except Exception as e:
        # If the stream fails halfway, clean up the corrupted partial file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="File upload failed")

    # 4. Save metadata to PostgreSQL
    db_file = FileAttachment(
        submission_id=submission_id,
        storage_path=file_path,
        original_filename=file.filename,
        mime_type=file.content_type,
        size_bytes=total_size
    )
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    
    return {"message": "File uploaded securely", "file_id": db_file.id}