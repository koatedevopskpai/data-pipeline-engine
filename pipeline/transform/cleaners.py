# All transform functions are pure: they take a dict, return a dict, no side effects.
# This is a deliberate architectural decision:
#
# 1. Composability: pure functions can be chained in any order, tested in isolation,
#    and combined into pipelines without shared state or hidden dependencies.
# 2. Testability: no mocking, no setup, no teardown. You call the function with
#    a dict and assert on the returned dict. This is why the tests are so simple.
# 3. Parallel safety: pure functions can run in parallel (map over records across
#    threads/processes) without locks, mutexes, or race conditions.
#
# The alternative would be a class-based transformer with mutable state (e.g.,
# tracking statistics across records). That would couple the transform logic to
# the pipeline execution model and make testing harder. Pure functions are the
# simpler, more correct choice for record-at-a-time transformations.

def drop_nulls(record: dict, fields: list[str] | None = None) -> dict:
    # If fields is None, drop ALL null-valued fields.
    # If fields is specified, only drop null in those specific fields.
    # This lets callers be aggressive (clean everything) or conservative
    # (only clean known-problematic fields) with the same function.
    fields = fields or list(record.keys())
    return {k: v for k, v in record.items() if k not in fields or v is not None}


def fill_missing(record: dict, fill_map: dict) -> dict:
    # fill_map maps field names to their default values.
    # We only fill if the field exists AND is None — missing fields entirely
    # are a separate concern handled by schema validation, not cleaning.
    # This separation of concerns (cleaning vs validation) is deliberate.
    result = dict(record)
    for field, default in fill_map.items():
        if field in result and result[field] is None:
            result[field] = default
    return result


def strip_whitespace(record: dict) -> dict:
    # Whitespace stripping must happen BEFORE validation. A string like "10 "
    # will fail a numeric validation, but after strip it becomes "10" which
    # can be coerced. Pipeline ordering matters.
    result = {}
    for k, v in record.items():
        if isinstance(v, str):
            result[k] = v.strip()
        else:
            result[k] = v
    return result
