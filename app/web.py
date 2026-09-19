from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates
from .dependencies import current_user
from .security import ensure_csrf
from .services.pricing import money, milli_to_quantity

TEMPLATE_DIR=Path(__file__).resolve().parent/'templates'
templates=Jinja2Templates(directory=str(TEMPLATE_DIR))
templates.env.filters['money']=money
templates.env.filters['qty']=milli_to_quantity

def render(request: Request, name: str, **context):
    context.update(request=request,current_user=current_user(request),csrf_token=ensure_csrf(request.session))
    return templates.TemplateResponse(request, name, context)

def flash(request: Request, message: str, kind='info'):
    request.session['flash']={'message':message,'kind':kind}

def pop_flash(request: Request):
    return request.session.pop('flash',None)
