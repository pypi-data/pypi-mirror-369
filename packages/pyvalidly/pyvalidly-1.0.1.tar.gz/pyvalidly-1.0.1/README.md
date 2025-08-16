# Pyvalidly

**Pyvalidly** is a lightweight, zero-dependency Python library for validating dictionaries with simple rules, custom functions, and optional coercion.

Inspired by Pydantic's power but built for simplicity, speed, and flexibility — especially useful when you want to avoid creating full-blown classes.

---

## Features

- Simple schema-based dictionary validation  
- Type validation – int, str, float, list, dict, custom classes.
- Coercion – Automatically convert types when possible.
- Default values – Fill missing fields with defaults.
- Conditional validation – Skip validation based on another field.
- Custom validation functions – Pass any callable returning True/False.
- Helper functions – is_email, is_url, min_value, max_value, min_length, max_length.
- Custom error messages – Per-field validation errors.
- Old-style and new-style schemas – Flexible for migration.

---

## Installation

```
pip install pyvalidly
```


## Basic Usage
### Old-style Schema
```
from pyvalidly import validate, is_email

schema = {
    "name": str, #(str,),
    "age": (int, lambda x: x > 18),
    "email": (str, is_email)
}

data = {
    "name": "John",
    "age": 25,
    "email": "john@example.com"
}

validated = validate(data, schema)
print(validated)
# {'name': 'John', 'age': 25, 'email': 'john@example.com'}


```

### New-style Schema

```
from pyvalidly import validate, is_email, min_value

schema = {
    "name": {"type": str, "required": True},
    "age": {"type": int, "coerce": True, "rules": [min_value(18)]},
    "email": {"type": str, "rules": [is_email]}
}

data = {
    "name": "John",
    "age": "42",
    "email": "john@example.com"
}

validated = validate(data,schema)
print(validated)
# {'name': 'John', 'age': 42, 'email': 'john@example.com'}

```

## Advanced Features
### 1. Type Coercion
```
from pyvalidly import validate, is_email, min_value

schema = {
    "age": {"type": int, "coerce": True}
}
data = {"age": "30"}

print(validate(data,schema))
# {'age': 30}

```

### 2. Default Values

```
from pyvalidly import validate, is_email, min_value

schema = {
    "name": {"type": str, "default": "Anonymous"}
}
data = {}

print(validate(data,schema))
# {'name': 'Anonymous'}

```

### 3. Conditional Validation

```
from pyvalidly import validate, is_email, min_value

schema = {
    "is_member": {"type": bool, "required": True},
    "membership_id": {
        "type": str,
        "required": True,
        "condition": lambda data: data.get("is_member") is True
    }
}

data = {"is_member": False}
print(validate(data, schema))
# {'is_member': False}

```

### 4. Custom Error Messages

```
from pyvalidly import validate, is_email, min_value
schema = {
    "age": {
        "type": int,
        "rules": [lambda x: x >= 18],
        "error": "Must be at least 18 years old"
    }
}
data = {"age": 10}

from pyvalidly.exceptions import ValidationError
try:
    print(validate(data, schema))
except ValidationError as e:
    print(e)
# Must be at least 18 years old

```

### 5. Built-in Helpers

```
from pyvalidly import is_email, is_url, min_value, max_value, min_length, max_length

print(is_email("test@example.com")) # True
print(is_url("http://example.com")) # True
print(min_value(10)(15)) # True
print(max_length(5)("hello")) # True

```

## Schema Styles

- Old-style tuple rules : 
Each field maps to a tuple of rules: (type, func, func, ...)

- New-style dict rules :
{ "type": str, "required": True, "default": "X", "rules": [func], "coerce": True, "condition": func }

## Project Structure
```
pyvalidly/
├── core.py
├── exceptions.py
├── validators.py
├── __init__.py
└── tests/
    └── test_core.py
```

## License

MIT License

## Contribute

Pull requests, suggestions, and stars are welcome!
If this helped you, consider supporting the project.

## Contact

Made with love by Deepak singh — https://github.com/dark00infinity