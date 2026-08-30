import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form as FormData
from sqlmodel import Session, select
from uuid import UUID, uuid4
from ..database import get_session
from ..models import FileAttachment, Form, FormSubmission, User
from ..dependencies import get_current_user

router = APIRouter(prefix="/files", tags=["Files"])

# In production, this would be an S3 bucket path.
UPLOAD_DIR = "secure_storage_vault/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png", "video/mp4"}
MAX_FILE_SIZE_MB = 100

def _matches_file_signature(content: bytes, mime_type: str) -> bool:
    return (
        (mime_type == "application/pdf" and content.startswith(b"%PDF-"))
        or (mime_type == "image/jpeg" and content.startswith(b"\xff\xd8\xff"))
        or (mime_type == "image/png" and content.startswith(b"\x89PNG\r\n\x1a\n"))
        or (mime_type == "video/mp4" and len(content) >= 12 and content[4:8] == b"ftyp")
    )

@router.post("/upload/{submission_id}")
async def upload_attachment(
    submission_id: UUID,
    # UploadFile automatically handles the multipart/form-data parsing
    file: UploadFile = File(...), 
    field_id: str = FormData(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Immediate Security Validations
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported file type.")
    submission = session.get(FormSubmission, submission_id)
    form = session.get(Form, submission.form_id) if submission else None
    if not form or form.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Submission not found")
    header = await file.read(16)
    if not _matches_file_signature(header, file.content_type):
        raise HTTPException(status_code=415, detail="File content does not match its declared type")
    
    # 2. Obfuscate the filename to prevent directory traversal attacks
    secure_filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, secure_filename)
    
    total_size = 0
    
    # 3. Stream the file directly to disk asynchronously using 'aiofiles'
    # This prevents the server from freezing while waiting for disk I/O
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(header)
            total_size = len(header)
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
        field_id=field_id,
        storage_path=file_path,
        original_filename=file.filename,
        mime_type=file.content_type,
        size_bytes=total_size
    )
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    
    return {"message": "File uploaded securely", "file_id": db_file.id}
