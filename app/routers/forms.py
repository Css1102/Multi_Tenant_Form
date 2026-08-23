import os
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import FileAttachment, Form, FormSubmission, User
from ..dependencies import get_current_user

router = APIRouter(prefix="/forms", tags=["Forms"])

@router.post("/", response_model=Form)
def create_form(
    form: Form, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    """Creates a form strictly bound to the user's organization."""
    if current_user.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Only owners and admins can create forms")
    # Force the form to belong to the user's tenant
    form.organization_id = current_user.organization_id
    form.created_by_user_id = current_user.id
    session.add(form)
    session.commit()
    session.refresh(form)
    return form

@router.get("/", response_model=List[Form])
def get_tenant_forms(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # Security Injection!
):
    """Fetches ONLY the forms belonging to the user's organization."""
    statement = select(Form).where(Form.organization_id == current_user.organization_id)
    forms = session.exec(statement).all()
    return forms


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form(
    form_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete a form and its responses; only its creator may do so."""
    form = session.get(Form, form_id)
    if not form or form.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Form not found")
    if form.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the form creator can delete it")
    try:
        submissions = session.exec(
            select(FormSubmission).where(FormSubmission.form_id == form_id)
        ).all()
        submission_ids = [submission.id for submission in submissions]
        attachments = (
            session.exec(
                select(FileAttachment).where(FileAttachment.submission_id.in_(submission_ids))
            ).all()
            if submission_ids
            else []
        )
        attachment_paths = [attachment.storage_path for attachment in attachments]

        for attachment in attachments:
            session.delete(attachment)
        for submission in submissions:
            session.delete(submission)
        # These tables have no ORM relationships, so explicitly flush child
        # deletes before scheduling the parent form deletion.
        session.flush()
        session.delete(form)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Could not delete form")

    storage_root = Path("secure_storage_vault").resolve()
    for attachment_path in attachment_paths:
        path = Path(attachment_path).resolve()
        if path.is_relative_to(storage_root) and path.exists():
            os.remove(path)
