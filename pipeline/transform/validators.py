# ValidationResult uses an accumulate-all-errors approach rather than fail-fast.
# This is a deliberate choice for data engineering:
#
# In a transaction processing system (e.g., payment processing), fail-fast is
# correct — one bad record should stop the batch before any damage is done.
#
# In a data pipeline, accumulate-all-errors is correct because:
# 1. Data quality reporting: you want to know EVERY record that failed,
#    not just the first one. A pipeline that reports "48 records failed schema
#    validation" is more useful than one that reports "record 1 failed, stopped."
# 2. Partial writes: many data pipelines accept partial success — write the
#    good records and quarantine the bad ones. Accumulating all errors lets
#    the caller decide this policy, not the validator.
# 3. Debugging: seeing all validation failures in one run is faster than
#    fix-one-record → rerun → fix-next-record cycles.
#
# The downside is that ValidationResult is slightly more complex than a boolean.
# The upside is that it carries actionable information — which fields failed,
# and why — rather than just "valid/invalid."

class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)


def validate_schema(record: dict, expected_fields: dict[str, type]) -> ValidationResult:
    # expected_fields is a dict of {field_name: Python_type}.
    # We check both presence (field exists) AND type (field has correct type).
    # None values skip type checking because None is a valid "missing data"
    # signal that should be handled by the cleaner, not the validator.
    result = ValidationResult()
    for field, expected_type in expected_fields.items():
        if field not in record:
            result.add_error(f"Missing field: {field}")
        elif record[field] is not None and not isinstance(record[field], expected_type):
            result.add_error(f"Field {field}: expected {expected_type.__name__}, got {type(record[field]).__name__}")
    return result


def validate_numeric_range(
    record: dict, field: str,
    min_val: float | None = None,
    max_val: float | None = None,
) -> ValidationResult:
    # Separate range validation from schema validation because they have
    # different error semantics. A missing field is a structural problem.
    # A field outside range is a business logic problem. Different teams
    # own different validation rules.
    result = ValidationResult()
    val = record.get(field)
    if val is None:
        return result
    try:
        num = float(val)
    except (TypeError, ValueError):
        result.add_error(f"Field {field}: not a numeric value")
        return result
    if min_val is not None and num < min_val:
        result.add_error(f"Field {field}: {num} is below minimum {min_val}")
    if max_val is not None and num > max_val:
        result.add_error(f"Field {field}: {num} exceeds maximum {max_val}")
    return result
