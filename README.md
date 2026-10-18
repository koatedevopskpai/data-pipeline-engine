# Data Pipeline Engine

An ETL reference pipeline demonstrating modern data engineering patterns: extract, transform, load across multiple source types, with a FastAPI serving layer, Streamlit observability dashboard, Docker containerisation, and CI/CD.

## Architecture

```
Data Sources ──▶ Extract ──▶ Transform ──▶ Load ──▶ API ──▶ Dashboard
  CSV/JSON         │             │            │         │
  APIs             │             │            │         │
  SQLite           │             │            │         │
                   ▼             ▼            ▼         ▼
              Source       Validated     Target     REST
              Readers      Cleaners      Writers    Endpoints
                          Aggregators
```

## Features

- **Multi-source extraction**: CSV files, JSON files, SQLite databases, REST APIs
- **Pipeline transformations**: Data cleaning, schema validation, field mapping, aggregation
- **Multiple load targets**: SQLite, PostgreSQL (configurable), CSV export
- **Pipeline metadata**: Every run is tracked with timestamps, row counts, status, and error logs
- **FastAPI serving layer**: Query pipeline history, browse loaded data, trigger pipeline runs
- **Streamlit dashboard**: Pipeline health monitoring, run history visualisation, data profiling
- **Docker containerised**: Multi-service setup with health checks and environment configuration
- **CI/CD via GitHub Actions**: Automated testing on push/PR

## Quick Start

```bash
# Clone and run
git clone https://github.com/koatedevopskpai/data-pipeline-engine.git
cd data-pipeline-engine
docker compose up --build

# Run pipeline manually
docker compose exec api python -m pipeline.run
```

## Project Structure

```
data-pipeline-engine/
├── pipeline/           # Core ETL logic
│   ├── extract/        # Source readers (CSV, JSON, API, SQLite)
│   ├── transform/      # Data cleaners, validators, aggregators
│   ├── load/           # Target writers (SQLite, PostgreSQL, CSV)
│   ├── models.py       # Pydantic data models
│   ├── config.py       # Environment-based configuration
│   └── run.py          # Pipeline orchestrator
├── api/                # FastAPI serving layer
│   ├── main.py         # App factory, routes
│   ├── schemas.py      # Request/response schemas
│   └── routes.py       # Endpoints
├── dashboard/          # Streamlit monitoring UI
│   └── app.py
├── data/               # Sample data for demo
│   └── sample/
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   ├── test_load.py
│   └── test_pipeline.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .github/workflows/ci.yml
└── pyproject.toml
```


## Claim review — 18 October 2026

See [verification and limits](evidence/W5-02.md) for the source revision, claim
classification and observed CI status. Wording corrections do not establish a
new deployment, passing test suite or production operation.
