import tempfile
from pathlib import Path

from pipeline.load.sqlite_target import SqliteTarget
from pipeline.load.csv_target import CsvTarget


def test_sqlite_write_and_fetch():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "test.db")
        target = SqliteTarget(db_path)
        records = [{"name": "alpha", "value": 10}, {"name": "beta", "value": 20}]
        written = target.write(records, "test_table")
        assert written == 2

        fetched = target.fetch_all("test_table")
        assert len(fetched) == 2
        assert fetched[0]["name"] == "alpha"
        target.close()


def test_sqlite_write_empty():
    with tempfile.TemporaryDirectory() as tmp:
        target = SqliteTarget(str(Path(tmp) / "test.db"))
        written = target.write([], "empty_table")
        assert written == 0
        target.close()


def test_csv_write():
    with tempfile.TemporaryDirectory() as tmp:
        target = CsvTarget(tmp)
        records = [{"name": "alpha", "value": "10"}, {"name": "beta", "value": "20"}]
        written = target.write(records, "test_export")
        assert written == 2

        out_path = Path(tmp) / "test_export.csv"
        assert out_path.exists()
        target.close()
