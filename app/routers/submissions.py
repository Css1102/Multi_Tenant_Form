import os
import json
import redis
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from uuid import UUID
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified
from pydantic import BaseModel
from ..database import get_session
from datetime import datetime, timezone
from ..models import Form, FormSubmission, User, FormField
from ..dependencies import get_current_user
from ..validator import validate_submission_data
from ..redis_client import sync_redis
# Import the limiter from our main setup
from slowapi import Limiter
from slowapi.util import get_remote_address
router = APIRouter(prefix="/submissions", tags=["Submissions"])
limiter = Limiter(key_func=get_remote_address)
# Initialize the Redis connection
# In production, fallback to "redis://localhost:6379/0" if REDIS_URL is not set
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
class SubmissionRequest(BaseModel):
    form_id: UUID
    answers: Dict[str, Any]

@router.post("/", response_model=FormSubmission)
@limiter.limit("30/minute") 
def submit_form(
    request: Request,
    payload: SubmissionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    form_id_str = str(payload.form_id)
    cache_key = f"form_schema:{form_id_str}"
    
    # 1. THE REDIS CACHE LAYER
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        form_dict = json.loads(cached_data)
        # Convert dicts back into Pydantic models for validation
        schema = [FormField(**field) for field in form_dict["structure"]]
        form_org_id = form_dict["organization_id"]
        form_is_active = form_dict.get("is_active", False)
        
    else:
        form = session.get(Form, payload.form_id)
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
            
        # FIX 1: Convert SQLAlchemy's dicts into Pydantic models for validation
        schema = [FormField(**field) for field in form.structure]
        form_org_id = str(form.organization_id)
        form_is_active = form.is_active
        
        # FIX 2: form.structure is ALREADY a list of dicts, no model_dump() needed!
        cache_payload = {
            "structure": form.structure, 
            "organization_id": form_org_id,
            "is_active": form_is_active,
        }
        redis_client.setex(cache_key, 600, json.dumps(cache_payload))

    # 2. THE SECURITY BOUNDARY
    if form_org_id != str(current_user.organization_id):
        raise HTTPException(status_code=403, detail="Form not found within your organization")
    if not form_is_active:
        raise HTTPException(status_code=409, detail="This form is no longer accepting submissions")

    existing_submission = session.exec(
        select(FormSubmission).where(
            FormSubmission.form_id == payload.form_id,
            FormSubmission.submitted_by_user_id == current_user.id,
        )
    ).first()
    if existing_submission:
        raise HTTPException(status_code=409, detail="You have already submitted this form")

    # 3. THE RUNTIME ENGINE
    validate_submission_data(schema=schema, answers=payload.answers)

    # 4. SAVE THE SUBMISSION
    db_submission = FormSubmission(
        form_id=payload.form_id,
        answers=payload.answers,
        submitted_by_user_id=current_user.id,
    )
    session.add(db_submission)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="You have already submitted this form")
    session.refresh(db_submission)
    
    # 5. REAL-TIME BROADCAST
    event_payload = {
        "event": "new_submission",
        "submission_id": str(db_submission.id),
        "form_id": str(db_submission.form_id),
        "timestamp": db_submission.created_at.isoformat()
    }

    channel_name = f"tenant_{form_org_id}_events"
    sync_redis.publish(channel_name, json.dumps(event_payload))
    
    return db_submission


@router.get("/forms/{form_id}/my-status")
def get_my_submission_status(
    form_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Return whether the current user may still submit this tenant form."""
    form = session.get(Form, form_id)
    if not form or form.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Form not found")

    has_submitted = session.exec(
        select(FormSubmission.id).where(
            FormSubmission.form_id == form_id,
            FormSubmission.submitted_by_user_id == current_user.id,
        )
    ).first() is not None
    return {"has_submitted": has_submitted, "is_active": form.is_active}

class UpdateSubmissionRequest(BaseModel):
    answers: Dict[str, Any]

@router.patch("/{submission_id}", response_model=FormSubmission)
def update_submission(
    submission_id: UUID,
    payload: UpdateSubmissionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Partially updates a form submission. 
    Merges new answers with existing ones and re-validates against the dynamic schema.
    """
    
    db_submission = session.get(FormSubmission, submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    form = session.get(Form, db_submission.form_id)
    if not form or str(form.organization_id) != str(current_user.organization_id):
        raise HTTPException(status_code=403, detail="Unauthorized to modify this submission")

    # 3. Merge the new answers into the existing JSONB data (The PATCH behavior)min_length
    # Using python dictionary unpacking: {**old, **new}
    updated_answers = {**db_submission.answers, **payload.answers}

    # 4. Re-run the Runtime Validation Engine!
    # Even on an update, we must ensure the new data doesn't violate rules (e.g. )
    validate_submission_data(schema=form.structure, answers=updated_answers)

    # 5. Save the updates to PostgreSQL
    db_submission.answers = updated_answers
    
    # Explicitly tell SQLAlchemy that the JSONB column was modified so it triggers an UPDATE statement
    flag_modified(db_submission, "answers") 
    
    session.add(db_submission)
    session.commit()
    session.refresh(db_submission)
    
    # 6. Real-Time Streaming: Broadcast the update to the SSE channel!
    event_payload = {
        "event": "submission_updated",
        "submission_id": str(db_submission.id),
        "form_id": str(db_submission.form_id),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    channel_name = f"tenant_{form.organization_id}_events"
    sync_redis.publish(channel_name, json.dumps(event_payload))
    
    return db_submission
