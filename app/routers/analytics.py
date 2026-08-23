import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func
from typing import Optional
from uuid import UUID
from ..database import get_session
from ..models import FormSubmission, Form, User
from ..dependencies import get_current_user
from ..redis_client import async_redis

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _get_tenant_form(session: Session, form_id: UUID, current_user: User) -> Form:
    """Load a form only when it belongs to the authenticated tenant."""
    form = session.get(Form, form_id)
    if not form or form.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Form not found")
    return form


def _get_creator_form(session: Session, form_id: UUID, current_user: User) -> Form:
    form = _get_tenant_form(session, form_id, current_user)
    if form.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the form creator can view responses")
    return form

@router.get("/submissions/{form_id}")
def get_form_submissions(
    form_id: UUID,
    # Pagination Parameters
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(50, le=100, description="Max records to return"),
    # Dynamic JSONB Filter (Passed as a JSON string in the query params)
    filter_criteria: Optional[str] = Query(None, description='JSON string, e.g. {"field_age_02": 26}'),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Enforce the Multi-Tenant Boundary First!
    # Never query submissions without verifying the user owns the parent form.
    _get_creator_form(session, form_id, current_user)

    # 2. Build the Base Query
    statement = select(FormSubmission).where(FormSubmission.form_id == form_id)

    # 3. Apply the JSONB Containment Filter (The Magic Step)
    # If the user asks for {"status": "approved"}, we use Postgres @> operator
    if filter_criteria:
        import json
        try:
            parsed_filter = json.loads(filter_criteria)
            # SQLAlchemy translates this into a native Postgres GIN index query
            statement = statement.where(FormSubmission.answers.contains(parsed_filter))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON filter criteria")

    # 4. Execute Pagination and Sorting
    statement = statement.order_by(FormSubmission.created_at.desc()).offset(skip).limit(limit)
    submissions = session.exec(statement).all()

    # 5. Get Total Count (for the frontend pagination UI)
    count_statement = select(func.count()).select_from(FormSubmission).where(FormSubmission.form_id == form_id)
    if filter_criteria:
        count_statement = count_statement.where(FormSubmission.answers.contains(parsed_filter))
    total_count = session.exec(count_statement).one()

    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "data": submissions
    }


@router.get("/forms/{form_id}/summary")
def get_form_summary(
    form_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Return the current aggregate values used by a form analytics view."""
    _get_creator_form(session, form_id, current_user)
    total, last_submission_at = session.exec(
        select(func.count(FormSubmission.id), func.max(FormSubmission.created_at))
        .where(FormSubmission.form_id == form_id)
    ).one()
    return {
        "form_id": form_id,
        "total_submissions": total,
        "last_submission_at": last_submission_at,
    }


@router.get("/forms/{form_id}/events")
async def form_live_events(
    form_id: UUID,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Server-sent events for one authorized form's submission changes."""
    _get_creator_form(session, form_id, current_user)

    async def event_generator():
        pubsub = async_redis.pubsub()
        channel_name = f"tenant_{current_user.organization_id}_events"
        await pubsub.subscribe(channel_name)
        try:
            yield ": connected\n\n"
            while not await request.is_disconnected():
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message["type"] == "message":
                    payload = json.loads(message["data"])
                    if payload.get("form_id") == str(form_id):
                        event_name = payload.get("event", "analytics.updated")
                        yield f"event: {event_name}\ndata: {json.dumps(payload)}\n\n"
                else:
                    # Keep idle connections open through load balancers/proxies.
                    yield ": keepalive\n\n"
                await asyncio.sleep(0.1)
        finally:
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@router.get("/live-feed")
async def live_feed(request: Request, current_user: User = Depends(get_current_user)):
    async def event_generator():
        pubsub = async_redis.pubsub()
        channel_name = f"tenant_{current_user.organization_id}_events"
        
        await pubsub.subscribe(channel_name)
    
        try:
            while True:
                if await request.is_disconnected():
                    break  
                # Check Redis for a new message. (timeout=1.0 prevents blocking the loop entirely)
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message["type"] == "message":
                    # SSE format requires the prefix "data: " and two newline characters at the end
                    yield f"data: {message['data']}\n\n"
                # Yield control back to the FastAPI event loop so it can handle other API requests
                await asyncio.sleep(0.1)
                
        finally:
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
