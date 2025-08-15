"""
Wrapper around BAML's `jsonish` crate:
https://github.com/BoundaryML/baml/tree/canary/engine/baml-lib/jsonish

This module provides enhanced JSON-like parsing using a Rust backend that can handle:
- Missing quotes around keys
- Single quotes instead of double quotes
- Trailing commas
- BAML constructs like markdown blocks and unions
- Smart AnyOf candidate selection
"""

import json
import re
from typing import Type, TypeVar

from pydantic import BaseModel

from ._rust import parse_to_json

T = TypeVar("T", bound=BaseModel)


class ParseError(Exception):
    """Raised when parsing fails."""


def parse_to_model(raw_string: str, model_class: Type[T]) -> T:
    """
    Parse a JSON-like string into a Pydantic model using enhanced Rust parser.

    The enhanced parser can handle:
    - Missing quotes around keys
    - Single quotes instead of double quotes
    - Trailing commas
    - BAML constructs like markdown blocks and unions
    - Smart AnyOf candidate selection

    Args:
        raw_string: The JSON-like string to parse
        model_class: The Pydantic model class to instantiate

    Returns:
        An instance of model_class populated with the parsed data

    Raises:
        ParseError: If parsing fails or validation fails
    """
    try:
        return model_class(**json.loads(parse_to_json(raw_string)))
    except Exception as e:
        msg = f"Parsing {raw_string} failed for {model_class.__name__}: {e}"
        raise ParseError(msg) from e

__all__ = ["parse_to_json", "parse_to_model", "ParseError"]
