from fastapi import HTTPException
from typing import Dict, Any, List
from .models import FormField
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

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
            if field_value is None or field_value == "" or field_value == []:
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
        if field.type in {"text", "textarea"} and isinstance(field_value, str):
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
            elif validation and ((validation.min_value is not None and field_value < validation.min_value) or (validation.max_value is not None and field_value > validation.max_value)):
                errors.append({"loc": ["body", "answers", field_id], "msg": "Number is outside the allowed range.", "type": "value_error.number.range"})
        elif field.type == "email":
            try:
                validate_email(str(field_value), check_deliverability=False)
            except EmailNotValidError:
                errors.append({"loc": ["body", "answers", field_id], "msg": "Enter a valid email address.", "type": "value_error.email"})
        elif field.type == "datetime":
            try:
                datetime.fromisoformat(str(field_value).replace("Z", "+00:00"))
            except ValueError:
                errors.append({"loc": ["body", "answers", field_id], "msg": "Enter a valid date and time.", "type": "value_error.datetime"})
        elif field.type == "yes_no" and not isinstance(field_value, bool):
            errors.append({"loc": ["body", "answers", field_id], "msg": "Expected a yes/no answer.", "type": "type_error.boolean"})
        elif field.type in {"radio", "checkbox"}:
            options = field.options or []
            values = field_value if field.type == "checkbox" else [field_value]
            if not isinstance(values, list) or any(value not in options for value in values):
                errors.append({"loc": ["body", "answers", field_id], "msg": "Select one of the configured options.", "type": "value_error.option"})

    # If any validation guardrails were triggered, halt the request execution
    if errors:
        raise HTTPException(status_code=422, detail=errors)
