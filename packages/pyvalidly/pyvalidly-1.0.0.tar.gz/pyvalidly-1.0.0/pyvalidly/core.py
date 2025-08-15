from typing import Any, Callable, Dict, Iterable, Tuple, Union
from .exceptions import ValidationError
from .validations import (
    is_validation_func,
    build_rule_from_string,
)

SchemaRule = Union[type, Callable[[Any], bool], Tuple[type, Callable[[Any], bool]]]
FieldSchema = Union[
    SchemaRule,  # old style: str: type | callable | (type, callable)
    Dict[str, Any],  # new style: dict config
]

def _apply_callable_rule(value: Any, rule: Callable[[Any], bool]) -> bool:
    try:
        return bool(rule(value))
    except Exception:
        return False


def _apply_rule_spec(value: Any, rule_spec: Union[str, Callable[[Any], bool]]) -> bool:
    """Apply a rule spec which can be a callable or a string like 'min_length:3'."""
    if isinstance(rule_spec, str):
        rule_fn = build_rule_from_string(rule_spec)
        return _apply_callable_rule(value, rule_fn)
    elif callable(rule_spec):
        return _apply_callable_rule(value, rule_spec)
    else:
        raise ValidationError(f"Unsupported rule spec: {rule_spec!r}")


def _validate_old_style_field(field: str, rule: SchemaRule, value: Any, *, coerce: bool) -> Any:
    """
    Supports old API:
      - rule is a type -> isinstance
      - rule is a callable -> returns truthy
      - rule is (type, callable) -> both checks
    """
    # (type, callable)
    if isinstance(rule, tuple) and len(rule) == 2 and isinstance(rule[0], type) and callable(rule[1]):
        expected_type, predicate = rule
        if coerce:
            try:
                value = expected_type(value)
            except Exception:
                raise ValidationError(f"Field '{field}' coercion to {expected_type.__name__} failed")
        elif not isinstance(value, expected_type):
            raise ValidationError(f"Field '{field}' must be of type {expected_type.__name__}")
        if not _apply_callable_rule(value, predicate):
            raise ValidationError(f"Field '{field}' failed validation")
        return value

    # simple type
    if isinstance(rule, type):
        if coerce:
            try:
                value = rule(value)
            except Exception:
                raise ValidationError(f"Field '{field}' coercion to {rule.__name__} failed")
        elif not isinstance(value, rule):
            raise ValidationError(f"Field '{field}' must be of type {rule.__name__}")
        return value

    # pure callable (e.g., is_email)
    if callable(rule):
        if not _apply_callable_rule(value, rule):
            raise ValidationError(f"Field '{field}' failed validation")
        return value

    raise ValidationError(f"Unsupported rule for field '{field}': {rule!r}")


def _validate_new_style_field(
    field: str,
    cfg: Dict[str, Any],
    value: Any,
    *,
    data: Dict[str, Any],
) -> Any:
    """
    New schema dict API:
      {
        "type": str | int | ...,
        "rules": [callable | "min_length:3" | ...],
        "required": True/False,
        "default": ...,
        "condition": callable(data)->bool  # runs validations only if True
        "coerce": True | callable  # True => coerce to 'type'; callable => use as coercer
        "error": "Custom message"
      }
    """
    error_msg = cfg.get("error")

    # condition: if provided and False => skip validation, accept value as-is
    cond = cfg.get("condition")
    if callable(cond):
        try:
            if not cond(data):
                return value
        except Exception as e:
            raise ValidationError(error_msg or f"Condition check failed for '{field}': {e}")

    # Handle type + coercion
    expected_type = cfg.get("type")
    coerce_spec = cfg.get("coerce", False)

    if expected_type is not None and not isinstance(expected_type, type):
        raise ValidationError(f"Field '{field}': 'type' must be a Python type, got {type(expected_type).__name__}")

    if expected_type is not None:
        if coerce_spec is True:
            # Coerce via type constructor
            try:
                value = expected_type(value)
            except Exception as e:
                raise ValidationError(error_msg or f"Field '{field}' could not be coerced to {expected_type.__name__}: {e}")
        elif callable(coerce_spec):
            try:
                value = coerce_spec(value)
            except Exception as e:
                raise ValidationError(error_msg or f"Field '{field}' coercion failed: {e}")
        else:
            # no coercion => strict isinstance
            if not isinstance(value, expected_type):
                raise ValidationError(error_msg or f"Field '{field}' must be of type {expected_type.__name__}")

    # Apply rules (list of callables or strings like 'min_value:18')
    rules = cfg.get("rules", [])
    if not isinstance(rules, Iterable) or isinstance(rules, (str, bytes)):
        raise ValidationError(f"Field '{field}': 'rules' must be a list/iterable of rules")

    for rule_spec in rules:
        ok = _apply_rule_spec(value, rule_spec)
        if not ok:
            # Prefer custom error if provided
            if error_msg:
                raise ValidationError(error_msg)
            # Otherwise, attempt a generic message
            if isinstance(rule_spec, str):
                raise ValidationError(f"Field '{field}' failed rule '{rule_spec}'")
            # callable
            name = getattr(rule_spec, "__name__", None) or "custom_rule"
            raise ValidationError(f"Field '{field}' failed rule '{name}'")

    return value


def validate(
    data: Dict[str, Any],
    schema: Dict[str, FieldSchema],
    *,
    coerce: bool = False,
) -> Dict[str, Any]:
    """
    Validate `data` against `schema`.

    Supports two schema styles:

    1) Old, lightweight style (backward compatible with your tests):
        rules = {"email": is_email, "age": (int, lambda x: x >= 18)}
        validate(data, rules, coerce=True)

    2) New dict-config style per field:
        rules = {
          "email": {"type": str, "rules": ["is_email"], "required": False, "default": "no-reply@example.com"},
          "age": {"type": int, "coerce": True, "rules": ["min_value:18"], "error": "Age must be 18+"},
          "name": {"type": str, "rules": ["min_length:3"]},
        }

    Returns coerced/validated dict or raises ValidationError (first error encountered).
    """
    validated: Dict[str, Any] = {}
    # Pass-through any extra keys not in schema to the output unchanged
    # (so callers keep their payload intact). You can change this if you want strict mode.
    for k, v in data.items():
        validated[k] = v

    for field, rule in schema.items():
        # NEW STYLE (dict config)
        if isinstance(rule, dict):
            required = rule.get("required", True)
            has_value = field in data and data[field] is not None

            if not has_value:
                if required:
                    if "default" in rule:
                        validated[field] = rule["default"]
                        continue
                    # missing required
                    custom = rule.get("error")
                    raise ValidationError(custom or f"Missing required field: {field}")
                else:
                    # optional
                    if "default" in rule:
                        validated[field] = rule["default"]
                    # else leave as-is (missing)
                    continue

            value = data[field]
            new_val = _validate_new_style_field(field, rule, value, data=data)
            validated[field] = new_val
            continue

        # OLD STYLE (type / callable / (type, callable))
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

        value = data[field]
        new_val = _validate_old_style_field(field, rule, value, coerce=coerce)
        validated[field] = new_val

    return validated
