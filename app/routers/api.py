from fastapi import APIRouter,Request
from ..dependencies import require_role
from ..constants import ROLE_COORDINATOR,ROLE_PACKER
from ..db import one
from ..services.reporting_service import round_totals
from ..services.pricing import milli_to_quantity,money

router=APIRouter(prefix='/api')

@router.get('/health')
def health(): return {'status':'ok'}

@router.get('/rounds/{rid}/totals')
def totals_api(request:Request,rid:int):
    require_role(request,ROLE_COORDINATOR,ROLE_PACKER); rnd=one('SELECT * FROM rounds WHERE id=?',(rid,))
    return {'round':dict(rnd) if rnd else None,'products':[dict(x,quantity=milli_to_quantity(x['requested_milli'],x['sale_type']),total=money(x['total_cents'])) for x in round_totals(rid)]}
