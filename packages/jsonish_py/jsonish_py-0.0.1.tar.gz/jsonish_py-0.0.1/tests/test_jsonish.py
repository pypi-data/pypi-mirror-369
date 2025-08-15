import json
from pydantic import BaseModel
from typing import List, Optional

from jsonish_py._rust import parse_to_json
from jsonish_py import parse_to_model


def test_basic_json():
    input_str = '{"name": "John", "age": 30, "city": "New York"}'
    result = parse_to_json(input_str)
    parsed = json.loads(result)

    assert parsed["name"] == "John"
    assert parsed["age"] == 30
    assert parsed["city"] == "New York"


def test_json_with_arrays():
    input_str = '{"numbers": [1, 2, 3], "empty": []}'
    result = parse_to_json(input_str)
    parsed = json.loads(result)

    assert parsed["numbers"] == [1, 2, 3]
    assert parsed["empty"] == []


def test_nested_objects():
    input_str = '{"user": {"name": "Alice", "details": {"age": 25, "active": true}}}'
    result = parse_to_json(input_str)
    parsed = json.loads(result)

    assert parsed["user"]["name"] == "Alice"
    assert parsed["user"]["details"]["age"] == 25
    assert parsed["user"]["details"]["active"] is True


def test_primitive_types():
    input_str = '{"string": "hello", "number": 42, "float": 3.14, "boolean": false, "null_value": null}'
    result = parse_to_json(input_str)
    parsed = json.loads(result)

    assert parsed["string"] == "hello"
    assert parsed["number"] == 42
    assert parsed["float"] == 3.14
    assert parsed["boolean"] is False
    assert parsed["null_value"] is None


def test_empty_objects():
    result = parse_to_json('{}')
    assert json.loads(result) == {}
    result = parse_to_json('[]')
    assert json.loads(result) == []


def test_permissive_parsing():
    # Incomplete object becomes empty object
    result = parse_to_json('{"invalid": }')
    assert json.loads(result) == {}

    # Non-JSON text becomes a string
    result = parse_to_json('not json at all')
    assert json.loads(result) == "not json at all"

    # Empty string becomes empty string
    result = parse_to_json('')
    assert json.loads(result) == ""

    # Test some other edge cases
    result = parse_to_json('42')  # Just a number
    assert json.loads(result) == 42

    result = parse_to_json('true')  # Just a boolean
    assert json.loads(result) is True


def test_json_like_strings():
    result = parse_to_json("{'name': 'John'}")
    parsed = json.loads(result)
    assert parsed["name"] == "John"


def test_whitespace_handling():
    input_str = '''
    {
        "name"  :  "John" ,
        "age"   :  30

    }
    '''
    result = parse_to_json(input_str)
    parsed = json.loads(result)

    assert parsed["name"] == "John"
    assert parsed["age"] == 30


def test_unicode_strings():
    input_str = '{"emoji": "🌟", "unicode": "café", "chinese": "你好"}'
    result = parse_to_json(input_str)
    parsed = json.loads(result)

    assert parsed["emoji"] == "🌟"
    assert parsed["unicode"] == "café"
    assert parsed["chinese"] == "你好"


def test_large_numbers():
    input_str = '{"small": 0, "negative": -123, "large": 9999999999, "scientific": 1e10}'
    result = parse_to_json(input_str)
    parsed = json.loads(result)

    assert parsed["small"] == 0
    assert parsed["negative"] == -123
    assert parsed["large"] == 9999999999
    assert parsed["scientific"] == 1e10


class User(BaseModel):
    name: str
    age: int
    email: Optional[str] = None


class UserWithPosts(BaseModel):
    name: str
    age: int
    posts: List[str] = []


def test_parse_to_model_basic():
    input_str = '{"name": "Alice", "age": 25, "email": "alice@example.com"}'
    user = parse_to_model(input_str, User)

    assert user.name == "Alice"
    assert user.age == 25
    assert user.email == "alice@example.com"


def test_parse_to_model_with_defaults():
    input_str = '{"name": "Bob", "age": 30}'
    user = parse_to_model(input_str, User)

    assert user.name == "Bob"
    assert user.age == 30
    assert user.email is None

    input_str2 = '{"name": "Carol", "age": 28, "posts": ["Hello", "World"]}'
    user_with_posts = parse_to_model(input_str2, UserWithPosts)

    assert user_with_posts.name == "Carol"
    assert user_with_posts.age == 28
    assert user_with_posts.posts == ["Hello", "World"]
