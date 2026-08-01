from fastapi import HTTPException
from typing import Dict, Any, List
from .models import FormField

def validate_submission_data(schema: List[FormField], answers: Dict[str, Any]) -> None:
    """
    Validates user answers against a dynamic form schema at runtime.
    Raises an HTTP 422 error containing all structural failures if validation fails.
    """
    errors = []

    for field in schema:
        field_id = field.id
        field_value = answers.get(field_id)
        validation = field.validation

        # 1. Check if the field is required but missing or empty
        if validation and validation.required:
            if field_value is None or field_value == "":
                errors.append({
                    "loc": ["body", "answers", field_id],
                    "msg": f"Field '{field.label}' is required.",
                    "type": "value_error.missing"
                })
                continue  # Skip further validation for this missing field

        # If the field is optional and missing, skip validation
        if field_value is None:
            continue

        # 2. Enforce Type-Specific Constraints
        if field.type == "text" and isinstance(field_value, str):
            if validation:
                if validation.min_length and len(field_value) < validation.min_length:
                    errors.append({
                        "loc": ["body", "answers", field_id],
                        "msg": f"Minimum length is {validation.min_length} characters.",
                        "type": "value_error.any_str.min_length"
                    })
                if validation.max_length and len(field_value) > validation.max_length:
                    errors.append({
                        "loc": ["body", "answers", field_id],
                        "msg": f"Maximum length is {validation.max_length} characters.",
                        "type": "value_error.any_str.max_length"
                    })
                    
        elif field.type == "number":
            if not isinstance(field_value, (int, float)):
                errors.append({
                    "loc": ["body", "answers", field_id],
                    "msg": f"Expected a numeric value, received {type(field_value).__name__}.",
                    "type": "type_error.number"
                })

    # If any validation guardrails were triggered, halt the request execution
    if errors:
        raise HTTPException(status_code=422, detail=errors)