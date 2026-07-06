# Aggregators use Counter and defaultdict instead of manual loops because:
# 1. They're standard library — no additional dependencies
# 2. They're implemented in C — faster than pure Python dict manipulation
# 3. They express intent clearly: Counter == counting, defaultdict(float) == summing
#
# The try/except in sum_by_field is defensive: real-world data has type surprises.
# A record with value="N/A" instead of a number should not crash the entire
# aggregation — it should skip that record and move on. The alternative (pre-filtering
# all records for type correctness) would require a separate pass over the data.
from collections import Counter, defaultdict


def count_by_field(records: list[dict], field: str) -> dict:
    return dict(Counter(r.get(field) for r in records if r.get(field) is not None))


def sum_by_field(records: list[dict], group_field: str, sum_field: str) -> dict:
    totals: dict = defaultdict(float)
    for r in records:
        key = r.get(group_field)
        val = r.get(sum_field)
        if key is not None and val is not None:
            try:
                totals[key] += float(val)
            except (TypeError, ValueError):
                pass
    return dict(totals)
