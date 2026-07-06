# TargetWriter ABC mirrors SourceReader. Same design rationale:
# 1. Swap targets without changing pipeline logic — write to SQLite for dev,
#    PostgreSQL for staging, CSV for export, all using the same interface.
# 2. The close() method exists because some targets (databases, network sockets)
#    need explicit cleanup. CSV files don't, but the interface is consistent.
# 3. The return type int is the count of records written. This lets the pipeline
#    compare rows_read vs rows_written as a data quality signal. If 1000 records
#    went in but only 997 came out, something happened in the pipeline.
from abc import ABC, abstractmethod


class TargetWriter(ABC):
    @abstractmethod
    def write(self, records: list[dict], table_name: str) -> int:
        ...

    @abstractmethod
    def close(self) -> None:
        ...
