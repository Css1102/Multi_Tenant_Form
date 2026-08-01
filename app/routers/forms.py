from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Form,User
from ..dependencies import get_current_user

router = APIRouter(prefix="/forms", tags=["Forms"])

@router.post("/", response_model=Form)
def create_form(
    form: Form, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    """Creates a form strictly bound to the user's organization."""
    # Force the form to belong to the user's tenant
    form.organization_id = current_user.organization_id 
    print("Creating form for organization:", form.organization_id)
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