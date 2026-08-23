"""Tenant-safe form-submission exports."""

import csv
import io
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import get_current_user
from ..models import Form, FormField, FormSubmission, User

router = APIRouter(prefix="/exports", tags=["Exports"])


def _csv_value(value: object) -> str:
    """Keep structured JSON answers readable and valid in one CSV cell."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


@router.get("/forms/{form_id}.csv")
def export_form_submissions(
    form_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Download all submissions for one form as a UTF-8 CSV file."""
    form = session.get(Form, form_id)
    if not form or form.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Form not found")
    if form.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the form creator can export responses")

    submissions = session.exec(
        select(FormSubmission)
        .where(FormSubmission.form_id == form_id)
        .order_by(FormSubmission.created_at.asc())
    ).all()

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    # JSONB schemas are returned by SQLAlchemy as dictionaries; convert them
    # before accessing field attributes during CSV generation.
    fields = [field if isinstance(field, FormField) else FormField(**field) for field in form.structure]
    writer.writerow(["Submission ID", "Submitted At", *[field.label for field in fields]])

    for submission in submissions:
        writer.writerow(
            [
                str(submission.id),
                submission.created_at.isoformat(),
                *[_csv_value(submission.answers.get(field.id)) for field in fields],
            ]
        )

    filename = f"form-{form_id}-submissions.csv"
    return Response(
        content="\ufeff" + output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
