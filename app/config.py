import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _env(name, default):
    return os.getenv(name, default)

@dataclass(frozen=True)
class Settings:
    app_name: str = _env('APP_NAME', 'Greenhill Food Co-op')
    secret: str = _env('APP_SECRET', 'dev-only-change-me')
    db_path: Path = BASE_DIR / _env('APP_DB_PATH', 'data/greenhill.db')
    debug: bool = _env('APP_DEBUG', '0') == '1'

settings = Settings()
settings.db_path.parent.mkdir(parents=True, exist_ok=True)
