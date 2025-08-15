use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

#[pyfunction]
fn parse_to_json(raw_string: String) -> PyResult<String> {
    use baml_jsonish::jsonish::{parse, ParseOptions};

    // Parse using BAML's jsonish parser
    let parsed_value = parse(&raw_string, ParseOptions::default(), true)
        .map_err(|e| PyValueError::new_err(format!("Failed to parse JSON-like string: {}", e)))?;

    // Convert to JSON string
    let json_value = jsonish_value_to_json_value(&parsed_value)
        .map_err(|e| PyValueError::new_err(format!("Failed to convert to JSON: {}", e)))?;
    serde_json::to_string(&json_value)
        .map_err(|e| PyValueError::new_err(format!("Failed to serialize to JSON: {}", e)))
}

fn jsonish_value_to_json_value(value: &baml_jsonish::jsonish::Value) -> Result<serde_json::Value, serde_json::Error> {
    use baml_jsonish::jsonish::Value;
    use serde_json::Value as JsonValue;

    match value {
        Value::String(s, _) => Ok(JsonValue::String(s.clone())),
        Value::Number(n, _) => Ok(JsonValue::Number(n.clone())),
        Value::Boolean(b) => Ok(JsonValue::Bool(*b)),
        Value::Null => Ok(JsonValue::Null),
        Value::Object(obj, _) => {
            let mut map = serde_json::Map::new();
            for (key, val) in obj {
                let json_val = jsonish_value_to_json_value(val)?;
                map.insert(key.clone(), json_val);
            }
            Ok(JsonValue::Object(map))
        },
        Value::Array(arr, _) => {
            let mut vec = Vec::new();
            for item in arr {
                let json_val = jsonish_value_to_json_value(item)?;
                vec.push(json_val);
            }
            Ok(JsonValue::Array(vec))
        },
        Value::Markdown(_, content, _) => jsonish_value_to_json_value(content),
        Value::FixedJson(content, _) => jsonish_value_to_json_value(content),
        Value::AnyOf(values, primitive_fallback) => {
            if values.is_empty() {
                // Use primitive fallback if no candidates
                Ok(JsonValue::String(primitive_fallback.clone()))
            } else {
                // Pick the candidate with the highest information content
                let best = values.iter().max_by_key(|v| simple_score(v)).unwrap();
                jsonish_value_to_json_value(best)
            }
        }
    }
}

fn simple_score(value: &baml_jsonish::jsonish::Value) -> i32 {
    use baml_jsonish::jsonish::Value;

    match value {
        Value::Null => 0,
        Value::String(s, _) => s.len() as i32,
        Value::Number(_, _) => 50,
        Value::Boolean(_) => 30,
        Value::Array(items, _) => 100 + items.len() as i32 * 10,
        Value::Object(fields, _) => 200 + fields.len() as i32 * 20,
        Value::Markdown(_, inner, _) => simple_score(inner) + 1,
        Value::FixedJson(inner, _) => simple_score(inner) + 1,
        Value::AnyOf(inner, _) => inner.iter().map(simple_score).max().unwrap_or(0),
    }
}

#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_to_json, m)?)?;
    Ok(())
}
