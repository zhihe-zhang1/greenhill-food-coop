import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _env(name, default):
    return os.getenv(name, default)

def _env_int(name, default):
    raw = os.getenv(name)
    try:
        return int(raw) if raw not in (None, '') else int(default)
    except (TypeError, ValueError):
        return int(default)

@dataclass(frozen=True)
class Settings:
    app_name: str = _env('APP_NAME', 'Greenhill Food Co-op')
    secret: str = _env('APP_SECRET', 'dev-only-change-me')
    db_path: Path = BASE_DIR / _env('APP_DB_PATH', 'data/greenhill.db')
    debug: bool = _env('APP_DEBUG', '0') == '1'
    # The listen address is configuration, not a constant: a container must bind
    # 0.0.0.0 for the published port to work, while a development machine is safer
    # on loopback (DEF-004).
    host: str = _env('APP_HOST', '127.0.0.1')
    port: int = _env_int('APP_PORT', '8000')

settings = Settings()
settings.db_path.parent.mkdir(parents=True, exist_ok=True)
