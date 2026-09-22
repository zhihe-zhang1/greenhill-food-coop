from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from .config import settings
from .db import init_db,seed_demo
from .dependencies import current_user
from .web import render,pop_flash
from .routers import auth,member,coordinator,packing,api

@asynccontextmanager
async def lifespan(app):
    init_db(); seed_demo(); yield

app=FastAPI(title=settings.app_name,lifespan=lifespan)
app.add_middleware(SessionMiddleware,secret_key=settings.secret,https_only=False,same_site='lax',max_age=60*60*8)
app.mount('/static',StaticFiles(directory=str(Path(__file__).resolve().parent/'static')),name='static')
app.include_router(auth.router); app.include_router(member.router); app.include_router(coordinator.router); app.include_router(packing.router); app.include_router(api.router)


@app.get('/')
def home(request:Request):
    user=current_user(request)
    if not user: return RedirectResponse('/login',303)
    if user['role']=='member': return RedirectResponse('/member',303)
    if user['role']=='packer': return render(request,'home.html',flash=pop_flash(request))
    return RedirectResponse('/coordinator',303)

@app.exception_handler(403)
async def forbidden(request:Request,exc): return render(request,'errors/403.html'),403

@app.exception_handler(404)
async def not_found(request:Request,exc): return render(request,'errors/404.html'),404
