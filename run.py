import uvicorn
from app.config import settings

if __name__ == '__main__':
    # Host and port come from the environment so the same entry point works locally
    # (127.0.0.1) and inside a container (0.0.0.0). Binding to loopback inside a
    # container made the published port unreachable from the host (DEF-004).
    uvicorn.run('app.main:app', host=settings.host, port=settings.port, reload=False)
