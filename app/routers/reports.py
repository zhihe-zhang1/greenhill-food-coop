from fastapi import APIRouter,Request
from fastapi.responses import Response,RedirectResponse
from ..config import settings
from ..constants import ROLE_COORDINATOR
from ..db import one,all_rows
from ..dependencies import require_role
from ..services.csv_service import round_csv_text
from ..services.metrics_service import round_metrics
from ..services.reporting_service import round_totals
from ..web import render

router=APIRouter(prefix='/reports')

def guard(request): return require_role(request,ROLE_COORDINATOR)

@router.get('/round/{rid}')
def round_report(request:Request,rid:int):
    guard(request); rnd=one('SELECT * FROM rounds WHERE id=?',(rid,))
    if not rnd: return RedirectResponse('/coordinator/rounds',303)
    return render(request,'coordinator/round_report.html',round=rnd,metrics=round_metrics(rid),totals=round_totals(rid))

@router.get('/round/{rid}/csv')
def round_csv(request:Request,rid:int):
    guard(request); rnd=one('SELECT * FROM rounds WHERE id=?',(rid,))
    if not rnd: return Response('Round not found',status_code=404)
    content='\ufeff'+round_csv_text(rid)
    return Response(content,media_type='text/csv; charset=utf-8',headers={'Content-Disposition':f'attachment; filename="greenhill_round_{rnd["number"]}.csv"'})

@router.get('/release')
def release_readiness(request:Request):
    guard(request)
    checks=[
        ('Database schema','Ready','SQLite schema is created automatically at startup.'),
        ('Demo seed','Ready','Representative users, products and an open round are available.'),
        ('Automated tests','Ready','Run pytest -q before creating a release tag.'),
        ('Configuration','Ready','.env.example documents environment settings; secrets are not committed.'),
        ('Handover','Review','Confirm README and docs/HANDOVER.md before final acceptance.'),
    ]
    recent=all_rows('SELECT * FROM rounds ORDER BY number DESC LIMIT 5')
    return render(request,'coordinator/release.html',app_name=settings.app_name,checks=checks,rounds=recent)
