# pydantic-settings over raw os.environ because:
# 1. Type coercion: PIPELINE_BATCH_SIZE=500 becomes int 500, not str "500"
# 2. Env prefix: all pipeline configs live under PIPELINE_* — no namespace pollution
# 3. .env file support: keeps secrets out of docker-compose.yml for production
# 4. Self-documenting: every config field IS the documentation
#
# This follows the 12-factor app pattern: configuration stored in the environment.
# For a portfolio project, this means the pipeline can be deployed anywhere
# (Render, Fly.io, AWS ECS) with nothing but env vars — no code changes.
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    source_path: str = "data/sample"
    db_url: str = "sqlite:///data/pipeline.db"
    batch_size: int = 1000
    fail_on_error: bool = False
    log_level: str = "INFO"

    model_config = {"env_prefix": "PIPELINE_", "env_file": ".env"}
