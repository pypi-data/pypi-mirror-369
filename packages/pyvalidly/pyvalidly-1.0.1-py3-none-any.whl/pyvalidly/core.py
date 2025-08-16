from typing import Any, Callable, Dict, Iterable, Tuple, Union
from .exceptions import ValidationError
from .validations import (
    is_validation_func,
    build_rule_from_string,
)

SchemaRule = Union[type, Callable[[Any], bool], Tuple[type, Callable[[Any], bool]]]
FieldSchema = Union[
    SchemaRule,              # old style: type | callable | (type, callable)
    Dict[str, Any],          # new style: dict config
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
    Old API:
      - rule is a type -> isinstance
      - rule is a callable -> returns truthy
      - rule is (type, callable) -> both checks
      - rule is (T,) -> treat like T   (compat nicety)
    """
    # allow (T,) as just T
    if isinstance(rule, tuple) and len(rule) == 1:
        rule = rule[0]

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
        "condition": callable(data)->bool,
        "coerce": True | callable,
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
            if not isinstance(value, expected_type):
                raise ValidationError(error_msg or f"Field '{field}' must be of type {expected_type.__name__}")

    # Apply rules (list of callables or strings like 'min_value:18')
    rules = cfg.get("rules", [])
    if not isinstance(rules, Iterable) or isinstance(rules, (str, bytes)):
        raise ValidationError(f"Field '{field}': 'rules' must be a list/iterable of rules")

    for rule_spec in rules:
        ok = _apply_rule_spec(value, rule_spec)
        if not ok:
            if error_msg:
                raise ValidationError(error_msg)
            if isinstance(rule_spec, str):
                raise ValidationError(f"Field '{field}' failed rule '{rule_spec}'")
            name = getattr(rule_spec, "__name__", None) or "custom_rule"
            raise ValidationError(f"Field '{field}' failed rule '{name}'")

    return value


def validate(data: dict, schema: dict, *, coerce: bool = False) -> dict:
    """
    Validate data against schema (both old-style and new-style).

    Args:
        data (dict): Input data
        schema (dict): Validation schema
        coerce (bool): If True, coerce values to expected type in old-style schemas.
                       For new-style, prefer per-field "coerce" option.
    """
    errors: Dict[str, str] = {}
    validated_data: Dict[str, Any] = {}

    for field, rules in schema.items():
        # ----- OLD-STYLE FIELD -----
        if not isinstance(rules, dict):
            try:
                validated_data[field] = _validate_old_style_field(
                    field, rules, data.get(field), coerce=coerce
                )
            except ValidationError as e:
                errors[field] = str(e)
            continue

        # ----- NEW-STYLE FIELD -----

        # evaluate condition EARLY for missing fields
        cond = rules.get("condition")
        if field not in data:
            if callable(cond):
                try:
                    if not cond(data):
                        # condition false -> skip entirely (no required, no default)
                        continue
                except Exception as e:
                    errors[field] = f"Condition check failed: {str(e)}"
                    continue

            # condition true (or no condition) -> enforce default/required
            if "default" in rules:
                validated_data[field] = rules["default"]
                continue
            if rules.get("required", False):
                errors[field] = f"'{field}' is required"
            continue

        # present value -> let the new-style validator handle coerce/type/rules/condition
        value = data[field]
        try:
            validated_data[field] = _validate_new_style_field(field, rules, value, data=data)
        except ValidationError as e:
            errors[field] = str(e)

    if errors:
        raise ValidationError(errors)

    return validated_data

