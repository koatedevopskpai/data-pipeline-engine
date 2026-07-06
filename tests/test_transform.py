from pipeline.transform import drop_nulls, fill_missing, strip_whitespace
from pipeline.transform import validate_schema, validate_numeric_range
from pipeline.transform import count_by_field, sum_by_field


def test_drop_nulls():
    record = {"a": 1, "b": None, "c": "x"}
    result = drop_nulls(record)
    assert "b" not in result
    assert result["a"] == 1


def test_drop_nulls_specific_fields():
    record = {"a": 1, "b": None, "c": None}
    result = drop_nulls(record, fields=["c"])
    assert "c" not in result
    assert "b" in result


def test_fill_missing():
    record = {"a": 1, "b": None, "c": "x"}
    result = fill_missing(record, {"b": 0, "c": "default"})
    assert result["b"] == 0
    assert result["c"] == "x"


def test_strip_whitespace():
    record = {"a": "  hello  ", "b": 42}
    result = strip_whitespace(record)
    assert result["a"] == "hello"
    assert result["b"] == 42


def test_validate_schema_passes():
    record = {"name": "alpha", "age": 30}
    result = validate_schema(record, {"name": str, "age": int})
    assert result.is_valid


def test_validate_schema_fails():
    record = {"name": "alpha", "age": "thirty"}
    result = validate_schema(record, {"name": str, "age": int})
    assert not result.is_valid
    assert len(result.errors) > 0


def test_validate_numeric_range():
    record = {"value": 50}
    result = validate_numeric_range(record, "value", min_val=0, max_val=100)
    assert result.is_valid

    result = validate_numeric_range(record, "value", max_val=10)
    assert not result.is_valid


def test_count_by_field():
    records = [{"type": "a"}, {"type": "b"}, {"type": "a"}]
    result = count_by_field(records, "type")
    assert result == {"a": 2, "b": 1}


def test_sum_by_field():
    records = [{"cat": "x", "val": 10}, {"cat": "y", "val": 20}, {"cat": "x", "val": 5}]
    result = sum_by_field(records, "cat", "val")
    assert result == {"x": 15.0, "y": 20.0}
