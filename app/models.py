from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, Optional, Any, Dict
from uuid import UUID, uuid4
from datetime import datetime, timezone

# 1. Pydantic Models for JSON Validation (These don't create DB tables)
class FieldValidation(SQLModel):
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    required: bool = False

class FormField(SQLModel):
    id: str = Field(..., description="Unique field ID (e.g., 'field_123')")
    label: str
    type: str = Field(..., description="e.g., 'text', 'number', 'file'")
    validation: Optional[FieldValidation] = None


class Organization(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    organization_id: UUID = Field(foreign_key="organization.id")

class Form(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(index=True)
    organization_id: UUID = Field(foreign_key="organization.id")
    is_active: bool = Field(default=True)
    
    structure: List[FormField] = Field(default=[], sa_column=Column(JSONB))
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FormSubmission(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    form_id: UUID = Field(foreign_key="form.id", index=True)
    
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