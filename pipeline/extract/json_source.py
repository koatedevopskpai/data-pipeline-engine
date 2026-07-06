# JsonSource handles both JSON arrays (list of dicts) and single JSON objects.
# This is essential for real-world data engineering: some systems export arrays,
# others export line-delimited objects, others export a single wrapping object.
# Rather than forcing the caller to normalise, JsonSource normalises internally.
#
# We use the standard `json` library instead of `orjson` or `ujson` because:
# 1. Zero dependency overhead — json is in the stdlib
# 2. For portfolio-scale data (< 1M records), the performance difference is negligible
# 3. Adding orjson later is a drop-in swap that doesn't change the interface
#
# Like CsvSource, this reads the entire file into memory. For a production system
# handling multi-GB JSON files, you'd want ijson (iterative JSON parser) instead.
# For this portfolio project targeting mid-scale data engineering roles, the
# in-memory approach is appropriate and simpler to understand.
import json
from collections.abc import Iterator
from pathlib import Path

from .base import SourceReader


class JsonSource(SourceReader):
    source_type = "json"

    def read(self, source: str) -> Iterator[dict]:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"JSON source not found: {source}")
        if path.is_dir():
            for file in path.glob("*.json"):
                yield from self._read_file(file)
        else:
            yield from self._read_file(path)

    def _read_file(self, path: Path) -> Iterator[dict]:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            yield from data
        else:
            yield data
