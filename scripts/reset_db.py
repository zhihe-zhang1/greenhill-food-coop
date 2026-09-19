from pathlib import Path
from app.config import settings
from app.db import init_db,seed_demo
if settings.db_path.exists(): settings.db_path.unlink()
init_db(); seed_demo(); print(f'Reset demo database: {settings.db_path}')
