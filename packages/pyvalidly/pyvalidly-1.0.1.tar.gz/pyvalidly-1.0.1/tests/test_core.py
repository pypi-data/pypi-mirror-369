import pytest
from pyvalidly.core import validate
from pyvalidly.exceptions import ValidationError
from pyvalidly import validations


def test_type_validation_pass():
    schema = {"age": (int, lambda x: x > 0)}
    data = {"age": 25}
    result = validate(data, schema)
    assert result["age"] == 25


def test_type_validation_fail():
    schema = {"age": (int, lambda x: x > 0)}
    data = {"age": -5}
    with pytest.raises(ValidationError):
        validate(data, schema)


def test_type_mismatch_fail():
    schema = {"age": (int, lambda x: x > 0)}
    data = {"age": "25"}  # not int and coerce=False
    with pytest.raises(ValidationError):
        validate(data, schema)


def test_with_coerce_old_style():
    # coerce to str, then predicate checks .isdigit()
    schema = {"age": (str, lambda s: s.isdigit())}
    data = {"age": 25}
    result = validate(data, schema, coerce=True)
    assert result["age"] == "25"


def test_required_field_missing():
    schema = {
        "name": {"type": str, "required": True}
    }
    with pytest.raises(ValidationError):
        validate({}, schema)


def test_required_field_with_default():
    schema = {
        "name": {"type": str, "required": False, "default": "Anonymous"}
    }
    result = validate({}, schema)
    assert result["name"] == "Anonymous"


def test_type_check_and_coerce_new_style():
    schema = {
        "age": {"type": int, "coerce": True}
    }
    result = validate({"age": "42"}, schema)
    assert isinstance(result["age"], int)
    assert result["age"] == 42


def test_condition_skips_validation():
    schema = {
        "discount": {
            "type": int,
            "required": False,
            "condition": lambda data: data.get("is_member") is True
        }
    }
    # condition False -> field is ignored (not required)
    result = validate({"is_member": False}, schema)
    assert "discount" not in result

    # when condition True, value must satisfy type
    with pytest.raises(ValidationError):
        validate({"is_member": True, "discount": "10"}, schema)


def test_custom_error_message():
    schema = {
        "age": {"type": int, "rules": [lambda x: x >= 18], "error": "Must be adult"}
    }
    with pytest.raises(ValidationError) as exc:
        validate({"age": 10}, schema)
    assert "Must be adult" in str(exc.value)


# ---------- STRING RULES VIA validations.build_rule_from_string ----------

def test_min_value_string_rule():
    schema = {"age": {"type": int, "rules": ["min_value:18"]}}
    with pytest.raises(ValidationError):
        validate({"age": 15}, schema)
    assert validate({"age": 18}, schema)["age"] == 18


def test_max_value_string_rule():
    schema = {"score": {"type": int, "rules": ["max_value:100"]}}
    assert validate({"score": 99}, schema)["score"] == 99
    with pytest.raises(ValidationError):
        validate({"score": 120}, schema)


def test_min_length_string_rule():
    schema = {"username": {"type": str, "rules": ["min_length:3"]}}
    with pytest.raises(ValidationError):
        validate({"username": "ab"}, schema)


def test_max_length_string_rule():
    schema = {"username": {"type": str, "rules": ["max_length:5"]}}
    with pytest.raises(ValidationError):
        validate({"username": "abcdef"}, schema)


# ---------- BUILT-IN HELPERS ----------

def test_is_email_helper():
    schema = {"email": {"type": str, "rules": [validations.is_email]}}
    assert validate({"email": "test@example.com"}, schema)["email"] == "test@example.com"
    with pytest.raises(ValidationError):
        validate({"email": "bad-email"}, schema)


def test_is_url_helper():
    schema = {"website": {"type": str, "rules": [validations.is_url]}}
    assert validate({"website": "http://example.com"}, schema)["website"] == "http://example.com"
    with pytest.raises(ValidationError):
        validate({"website": "not-a-url"}, schema)


def test_multiple_rules_pass():
    schema = {
        "username": {
            "type": str,
            "rules": [validations.min_length(3), validations.max_length(10)]
        }
    }
    result = validate({"username": "validName"}, schema)
    assert result["username"] == "validName"


def test_multiple_rules_fail():
    schema = {
        "username": {
            "type": str,
            "rules": [validations.min_length(3), validations.max_length(5)]
        }
    }
    with pytest.raises(ValidationError):
        validate({"username": "toolongusername"}, schema)


def test_mixed_old_and_new_styles():
    schema = {
        "age": (int, lambda x: x > 0),  # old style
        "email": {"type": str, "rules": [validations.is_email]}  # new style
    }
    result = validate({"age": 25, "email": "me@example.com"}, schema)
    assert result["age"] == 25
    assert result["email"] == "me@example.com"
