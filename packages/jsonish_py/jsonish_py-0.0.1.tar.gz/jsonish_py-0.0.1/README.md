# jsonish_py

A Python wrapper around [BAML's jsonish crate](https://github.com/BoundaryML/baml/tree/canary/engine/baml-lib/jsonish) for flexible JSON-like parsing.

## Overview

This library uses BAML's Rust-based `jsonish` parser to handle malformed or non-standard JSON strings that regular parsers would reject. It provides two main functions:

- **`parse_to_json`** - Parses JSON-like strings into standard JSON
- **`parse_to_model`** - A utility that combines parsing with Pydantic model validation

## Installation

```bash
pip install jsonish_py
```

## Usage

### Basic JSON parsing

```python
import jsonish_py

# Standard JSON works fine
result = jsonish_py.parse_to_json('{"name": "John", "age": 30}')
# Returns: '{"name": "John", "age": 30}'

# But it also handles malformed JSON
result = jsonish_py.parse_to_json('{"name": John, "age": 30,}')  # Missing quotes, trailing comma
result = jsonish_py.parse_to_json("{'name': 'John'}")  # Single quotes
```

### Parsing to Pydantic models

```python
from pydantic import BaseModel
import jsonish_py

class User(BaseModel):
    name: str
    age: int

# Parse directly to a Pydantic model
user = jsonish_py.parse_to_model('{"name": "Alice", "age": 25}', User)
print(user.name)  # Alice
print(user.age)   # 25
```
