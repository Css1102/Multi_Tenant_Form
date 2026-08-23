from sqlmodel import SQLModel, Field
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Optional, Any, Dict
from uuid import UUID, uuid4
from datetime import datetime, timezone

# 1. Pydantic Models for JSON Validation (These don't create DB tables)
class FieldValidation(SQLModel):
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    required: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None

class FormField(SQLModel):
    id: str = Field(..., description="Unique field ID (e.g., 'field_123')")
    label: str
    type: str = Field(..., description="e.g., 'text', 'number', 'file'")
    options: Optional[List[str]] = None
    validation: Optional[FieldValidation] = None


class Organization(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # The database also enforces uniqueness on the normalized value during
    # startup migration; this index supports tenant lookup by name.
    name: str = Field(index=True, nullable=False)

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    organization_id: UUID = Field(foreign_key="organization.id")
    role: str = Field(default="member", index=True)

class OrganizationInvite(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", index=True)
    role: str = Field(default="member")
    used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Form(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(index=True)
    organization_id: UUID = Field(foreign_key="organization.id")
    created_by_user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", index=True)
    is_active: bool = Field(default=True)
    
    structure: List[FormField] = Field(default=[], sa_column=Column(JSONB))
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FormSubmission(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("form_id", "submitted_by_user_id", name="uq_form_submission_user"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    form_id: UUID = Field(foreign_key="form.id", index=True)
    submitted_by_user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", index=True)
    
    # Stores the raw answers as a key-value pair, e.g., {"field_name_01": "John Doe"}
    answers: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FileAttachment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    submission_id: UUID = Field(foreign_key="formsubmission.id", index=True)
    
    # Store the safe, obfuscated path where the file is actually located
    storage_path: str = Field(unique=True) 
    
    # Store the original name just for display purposes
    original_filename: str 
    mime_type: str
    size_bytes: int
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
