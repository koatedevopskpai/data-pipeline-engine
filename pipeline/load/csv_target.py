# CsvTarget uses the stdlib csv module rather than Pandas to_csv.
# Why? Writing CSV is simpler than reading CSV:
#   - No type inference needed — the data already has the right types
#   - No encoding detection — we control the output encoding
#   - Pandas would add overhead for a trivial write operation
#
# The pattern: use Pandas for READING (where type inference is valuable),
# use stdlib for WRITING (where we control the schema and just need serialisation).
# This is a pragmatic middle ground between "use Pandas for everything" (overkill)
# and "use stdlib for everything" (misses Pandas' value in extraction).
import csv
from pathlib import Path

from .base import TargetWriter


class CsvTarget(TargetWriter):
    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, records: list[dict], table_name: str) -> int:
        if not records:
            return 0
        path = self.output_dir / f"{table_name}.csv"
        columns = list(records[0].keys())
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(records)
        return len(records)

    def close(self) -> None:
        pass
