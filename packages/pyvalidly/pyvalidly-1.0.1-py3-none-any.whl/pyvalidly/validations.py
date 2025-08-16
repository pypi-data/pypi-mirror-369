import re
from urllib.parse import urlparse
from typing import Any, Callable, Dict

# ---------- Basic validators (callables) ----------

def is_email(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    # simple, permissive email check
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value) is not None

def is_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)

def is_alphanumeric(value: Any) -> bool:
    return isinstance(value, str) and value.isalnum()

def is_positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and value > 0

def is_negative(value: Any) -> bool:
    return isinstance(value, (int, float)) and value < 0

def matches_regex(pattern: str) -> Callable[[Any], bool]:
    reg = re.compile(pattern)
    def _inner(value: Any) -> bool:
        return isinstance(value, str) and reg.search(value) is not None
    _inner.__name__ = f"matches_regex:{pattern}"
    return _inner

def in_choices(*choices: Any) -> Callable[[Any], bool]:
    def _inner(value: Any) -> bool:
        return value in choices
    _inner.__name__ = f"in_choices:{','.join(map(str, choices))}"
    return _inner

def min_value(min_val: float) -> Callable[[Any], bool]:
    def _inner(value: Any) -> bool:
        return isinstance(value, (int, float)) and value >= min_val
    _inner.__name__ = f"min_value:{min_val}"
    return _inner

def max_value(max_val: float) -> Callable[[Any], bool]:
    def _inner(value: Any) -> bool:
        return isinstance(value, (int, float)) and value <= max_val
    _inner.__name__ = f"max_value:{max_val}"
    return _inner

def between(min_val: float, max_val: float) -> Callable[[Any], bool]:
    def _inner(value: Any) -> bool:
        return isinstance(value, (int, float)) and (min_val <= value <= max_val)
    _inner.__name__ = f"between:{min_val},{max_val}"
    return _inner

def min_length(min_len: int) -> Callable[[Any], bool]:
    def _inner(value: Any) -> bool:
        try:
            return len(value) >= min_len
        except Exception:
            return False
    _inner.__name__ = f"min_length:{min_len}"
    return _inner

def max_length(max_len: int) -> Callable[[Any], bool]:
    def _inner(value: Any) -> bool:
        try:
            return len(value) <= max_len
        except Exception:
            return False
    _inner.__name__ = f"max_length:{max_len}"
    return _inner

# ---------- Helpers ----------

def is_validation_func(obj: Any) -> bool:
    return callable(obj)

# Map of non-parameterized rule names -> callables
SIMPLE_RULES: Dict[str, Callable[[Any], bool]] = {
    "is_email": is_email,
    "is_url": is_url,
    "is_alphanumeric": is_alphanumeric,
    "is_positive": is_positive,
    "is_negative": is_negative,
}

# Map of parameterized rule factories
PARAM_RULE_FACTORIES: Dict[str, Callable[..., Callable[[Any], bool]]] = {
    "min_value": min_value,
    "max_value": max_value,
    "between": between,
    "min_length": min_length,
    "max_length": max_length,
    "matches_regex": matches_regex,
    "in_choices": in_choices,
}

def build_rule_from_string(rule_str: str) -> Callable[[Any], bool]:
    """
    Turn strings like:
      - "is_email"
      - "min_length:3"
      - "between:1,10"
      - "matches_regex:^foo"
      - "in_choices:RED,GREEN,BLUE"
    into validator callables.
    """
    if ":" not in rule_str:
        # simple rule without params
        if rule_str in SIMPLE_RULES:
            return SIMPLE_RULES[rule_str]
        raise ValueError(f"Unknown validation rule: '{rule_str}'")

    name, arg_str = rule_str.split(":", 1)
    name = name.strip()
    arg_str = arg_str.strip()

    if name not in PARAM_RULE_FACTORIES:
        raise ValueError(f"Unknown parametrized rule: '{name}'")

    # Special-case certain factories:
    if name == "matches_regex":
        return PARAM_RULE_FACTORIES[name](arg_str)

    if name == "in_choices":
        parts = [p.strip() for p in arg_str.split(",") if p.strip() != ""]
        return PARAM_RULE_FACTORIES[name](*parts)

    # numeric args (min_value, max_value, between, min_length, max_length)
    parts = [p.strip() for p in arg_str.split(",")]
    nums = []
    for p in parts:
        # try int, else float
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(float(p))
    return PARAM_RULE_FACTORIES[name](*nums)
