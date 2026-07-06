import json
import csv
import tempfile
from pathlib import Path

from pipeline.extract import CsvSource, JsonSource


def test_csv_source_reads_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.csv"
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "value"])
            writer.writeheader()
            writer.writerow({"name": "alpha", "value": "10"})
            writer.writerow({"name": "beta", "value": "20"})

        source = CsvSource()
        records = list(source.read(str(path)))
        assert len(records) == 2
        assert records[0]["name"] == "alpha"


def test_csv_source_missing_file():
    source = CsvSource()
    try:
        list(source.read("/nonexistent/file.csv"))
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_json_source_reads_list():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.json"
        data = [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}]
        with open(path, "w") as f:
            json.dump(data, f)

        source = JsonSource()
        records = list(source.read(str(path)))
        assert len(records) == 2
        assert records[0]["id"] == 1


def test_json_source_reads_single_object():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "single.json"
        data = {"id": 1, "name": "alpha"}
        with open(path, "w") as f:
            json.dump(data, f)

        source = JsonSource()
        records = list(source.read(str(path)))
        assert len(records) == 1
        assert records[0]["name"] == "alpha"
