import csv
import tempfile
from pathlib import Path

from pipeline.config import Settings
from pipeline.run import PipelineOrchestrator


def test_csv_pipeline_end_to_end():
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "source.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "value"])
            writer.writeheader()
            writer.writerow({"name": "alpha", "value": "10"})
            writer.writerow({"name": "beta", "value": "20"})

        db_path = str(Path(tmp) / "pipeline.db")
        settings = Settings(db_url=f"sqlite:///{db_path}", source_path=str(csv_path))
        orchestrator = PipelineOrchestrator(settings)
        result = orchestrator.run_csv_pipeline(table_name="test_results")

        assert result.status.value == "completed"
        assert result.rows_read == 2
        assert result.rows_written == 2
        assert result.error_log == []


def test_pipeline_tracks_errors():
    orchestrator = PipelineOrchestrator(Settings())
    result = orchestrator.run_csv_pipeline(source_path="/nonexistent/file.csv")
    assert result.status.value == "failed"
    assert len(result.error_log) > 0
