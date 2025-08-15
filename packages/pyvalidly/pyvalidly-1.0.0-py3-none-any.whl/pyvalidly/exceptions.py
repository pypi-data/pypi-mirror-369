from typing import Dict, Optional

class ValidationError(Exception):
    """
    Raised when validation fails. You can pass a message or a dict of field errors.
    """
    def __init__(self, message_or_errors: Optional[object] = None, errors: Optional[Dict[str, str]] = None):
        if isinstance(message_or_errors, dict) and errors is None:
            errors = message_or_errors
            message = "Validation failed"
        elif isinstance(message_or_errors, str) or message_or_errors is None:
            message = message_or_errors or "Validation failed"
        else:
            message = "Validation failed"

        super().__init__(message)
        self.message = message
        self.errors = errors or {}

    def __str__(self) -> str:
        if self.errors:
            details = ", ".join(f"{k}: {v}" for k, v in self.errors.items())
            return f"{self.message} ({details})"
        return self.message
