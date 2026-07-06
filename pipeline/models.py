# Pydantic for all data models. This is a deliberate choice: Pydantic gives us
# validation, serialization, JSON Schema generation, and self-documenting types
# without the ceremony of dataclasses + manual validation. For a data pipeline,
# having guaranteed-valid data at every boundary is non-negotiable.
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


# StrEnum classes so values serialize naturally to JSON API responses.
# No reason to make API consumers parse custom enum serialization.
class SourceType(str, Enum):
    csv = "csv"
    json = "json"
    sqlite = "sqlite"
    api = "api"


class LoadTarget(str, Enum):
    sqlite = "sqlite"
    postgres = "postgres"
    csv_export = "csv_export"


class PipelineStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


# DataRecord models a single record flowing through the pipeline.
# The `id` field is optional because records may not have an identifier
# at extraction time — they might come from a CSV without a primary key.
# Tracking `validated` and `errors` separately lets us separate the concerns
# of pipeline execution vs data quality. The pipeline moves data; validation
# annotates it. These are different responsibilities.
class DataRecord(BaseModel):
    id: str | None = None
    source: str
    raw: dict
    validated: bool = False
    errors: list[str] = Field(default_factory=list)


# PipelineRun is the audit record. Every pipeline execution produces one.
# We track both sides of the equation (rows_read vs rows_written) because
# a significant gap between them signals data quality issues in transformation.
# The error_log accumulates rather than fails fast — in batch processing,
# you want to know about ALL failures, not just the first one.
class PipelineRun(BaseModel):
    run_id: str
    source_type: SourceType
    target: LoadTarget
    status: PipelineStatus = PipelineStatus.pending
    started_at: datetime | None = None
    completed_at: datetime | None = None
    rows_read: int = 0
    rows_written: int = 0
    error_count: int = 0
    error_log: list[str] = Field(default_factory=list)


# PipelineConfig uses BaseModel (not pydantic-settings) because this is
# a composition-time configuration object, not an environment-bound one.
# The Settings class in config.py handles env-based config; this is for
# programmatic overrides when you want to configure a pipeline in code.
class PipelineConfig(BaseModel):
    source_path: str = "data/sample"
    db_url: str = "sqlite:///data/pipeline.db"
    batch_size: int = 1000
    fail_on_error: bool = False
