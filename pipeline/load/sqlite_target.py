# SqliteTarget uses raw SQL instead of SQLAlchemy ORM. Decision rationale:
#
# Raw SQL:
# + Shows I understand SQL — quoting, placeholders, table creation, transactions
# + Zero abstraction overhead — what you see is what the database executes
# + Lighter dependency — no SQLAlchemy import overhead
# - Manual column handling — ORM would infer schema from models
#
# SQLAlchemy ORM:
# + Schema migration tooling (Alembic)
# + Relationship loading, joined queries
# + Connection pooling, dialect abstraction
# - Hides SQL behind Python objects — masks whether I actually know SQL
# - Heavier dependency for a portfolio project
#
# For a portfolio project demonstrating data engineering fundamentals,
# raw SQL is the right choice. It proves I understand the underlying technology.
# The ORM is a productivity tool I can adopt when the schema complexity justifies it.
#
# One specific design decision: we use CREATE TABLE IF NOT EXISTS with the
# record's column names as the table schema. This is intentionally simple.
# A production system would use explicit schema definitions with types,
# constraints, and indexes. For this portfolio project, dynamic schema creation
# shows the pipeline adapts to any data — which is the more impressive demo.
import sqlite3
from pathlib import Path

from .base import TargetWriter


class SqliteTarget(TargetWriter):
    def __init__(self, db_path: str = "data/pipeline.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def write(self, records: list[dict], table_name: str) -> int:
        if not records:
            return 0
        columns = list(records[0].keys())
        placeholders = ", ".join("?" for _ in columns)
        col_names = ", ".join(f'"{c}"' for c in columns)
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({col_names})")
        rows = []
        for r in records:
            rows.append(tuple(r.get(c) for c in columns))
        self.cursor.executemany(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", rows)
        self.conn.commit()
        return len(rows)

    def fetch_all(self, table_name: str) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def close(self) -> None:
        self.conn.close()
