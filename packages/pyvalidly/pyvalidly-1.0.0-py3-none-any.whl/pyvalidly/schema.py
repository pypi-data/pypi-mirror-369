from typing import Any, Dict
from .core import validate

class Schema:
    """
    Wrapper over validate() to reuse schemas.

    Example:
        user = Schema({
            "name": {"type": str, "rules": ["min_length:3"]},
            "email": {"type": str, "rules": ["is_email"], "required": False, "default": "no-reply@example.com"},
            "age": {"type": int, "coerce": True, "rules": ["min_value:18"], "error": "Age must be 18+"}
        })

        user.validate(payload)  # returns validated dict or raises ValidationError
    """
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules

    def validate(self, data: Dict[str, Any], *, coerce: bool = False) -> Dict[str, Any]:
        # coerce is only used for the old-style schema rules
        return validate(data, self.rules, coerce=coerce)
