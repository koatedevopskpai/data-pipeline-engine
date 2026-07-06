import logging
import uuid
from datetime import datetime, timezone

from pipeline.config import Settings
from pipeline.extract import CsvSource, JsonSource, ApiSource
from pipeline.transform import drop_nulls, strip_whitespace
from pipeline.load import SqliteTarget, CsvTarget
from pipeline.models import PipelineRun, PipelineStatus

# PipelineOrchestrator is the single entry point for all pipeline execution.
# Why a dedicated orchestrator class instead of functions scattered across modules?
#
# 1. Single responsibility: the orchestrator controls the lifecycle — extraction,
#    transformation, and loading are delegated to specialised modules.
# 2. Audit trail: every pipeline run produces a PipelineRun record with timing,
#    row counts, and error logs. The orchestrator owns this because it's the
#    only component that sees the full picture.
# 3. Testability: you can instantiate an orchestrator with a test Settings,
#    run a pipeline on a temp CSV, and assert on the PipelineRun result.
#    No global state, no mocking framework needed.
#
# The _run method is private because the public API is the typed convenience
# methods (run_csv_pipeline, run_json_pipeline, run_api_pipeline). The caller
# should never need to know that these all delegate to the same internal method.
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self._runs: list[PipelineRun] = []

    def run_csv_pipeline(self, source_path: str | None = None, table_name: str = "records") -> PipelineRun:
        return self._run(
            source_type="csv",
            reader=CsvSource(),
            source=source_path or self.settings.source_path,
            target=SqliteTarget(self.settings.db_url.replace("sqlite:///", "")),
            table_name=table_name,
        )

    def run_json_pipeline(self, source_path: str, table_name: str = "json_records") -> PipelineRun:
        return self._run(
            source_type="json",
            reader=JsonSource(),
            source=source_path,
            target=SqliteTarget(self.settings.db_url.replace("sqlite:///", "")),
            table_name=table_name,
        )

    def run_api_pipeline(self, url: str, table_name: str = "api_records") -> PipelineRun:
        return self._run(
            source_type="api",
            reader=ApiSource(),
            source=url,
            target=SqliteTarget(self.settings.db_url.replace("sqlite:///", "")),
            table_name=table_name,
        )

    def _run(
        self,
        source_type: str,
        reader: object,
        source: str,
        target: SqliteTarget | CsvTarget,
        table_name: str,
    ) -> PipelineRun:
        run = PipelineRun(
            run_id=str(uuid.uuid4())[:8],
            source_type=source_type,
            target=type(target).__name__.replace("Target", "").lower(),
            status=PipelineStatus.running,
            started_at=datetime.now(timezone.utc),
        )

        try:
            records = list(reader.read(source))
            run.rows_read = len(records)

            # Transform pipeline: each function is a pure, composable step.
            # We execute strip_whitespace first because whitespace in string
            # fields can cause false positives in validation (e.g., "10 " != "10").
            # We execute drop_nulls second because null fields may be explicitly
            # required downstream — better to fail fast on missing data than
            # silently propagate None values into the target.
            cleaned = []
            for r in records:
                r = strip_whitespace(r)
                r = drop_nulls(r)
                cleaned.append(r)

            written = target.write(cleaned, table_name)
            target.close()
            run.rows_written = written
            run.status = PipelineStatus.completed
        except Exception as e:
            # Failures must never silently swallow. Even if the pipeline errors,
            # we return a PipelineRun with status="failed" and the error in the log.
            # This lets callers (API, dashboard, CI) handle failure uniformly.
            run.status = PipelineStatus.failed
            run.error_log.append(str(e))
            logger.exception("Pipeline run failed")

        run.completed_at = datetime.now(timezone.utc)
        self._runs.append(run)
        return run

    def get_runs(self) -> list[PipelineRun]:
        # Return a copy to prevent external mutation of the internal run history.
        return list(self._runs)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    orchestrator = PipelineOrchestrator()

    result = orchestrator.run_csv_pipeline()
    print(f"Run {result.run_id}: {result.status.value} | Read: {result.rows_read} | Written: {result.rows_written}")


if __name__ == "__main__":
    main()
