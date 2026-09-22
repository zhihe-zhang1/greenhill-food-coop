from fastapi import APIRouter,Request,Form
from fastapi.responses import RedirectResponse
from ..dependencies import require_role
from ..constants import ROLE_COORDINATOR,ROLE_PACKER
from ..db import one,execute
from ..security import valid_csrf
from ..services.pricing import quantity_to_milli
from ..services.reporting_service import packing_rows
from ..services.audit_service import audit
from ..web import render,flash,pop_flash

router=APIRouter(prefix='/packing')

def guard(request): return require_role(request,ROLE_COORDINATOR,ROLE_PACKER)

@router.get('/round/{rid}')
def sheet(request:Request,rid:int):
    guard(request); return render(request,'packing/sheet.html',round=one('SELECT * FROM rounds WHERE id=?',(rid,)),rows=packing_rows(rid),flash=pop_flash(request))

@router.post('/line/{line_id}')
def update_line(request:Request,line_id:int,packed_qty:str=Form(...),initials:str=Form(''),note:str=Form(''),csrf_token:str=Form(...)):
    user=guard(request); row=one('''SELECT ol.*,p.sale_type,o.round_id FROM order_lines ol JOIN round_products rp ON rp.id=ol.round_product_id JOIN products p ON p.id=rp.product_id JOIN orders o ON o.id=ol.order_id WHERE ol.id=?''',(line_id,))
    if row and valid_csrf(request.session,csrf_token):
        try:
            milli=quantity_to_milli(packed_qty,row['sale_type']); execute('UPDATE order_lines SET packed_milli=?,packer_initials=?,note=? WHERE id=?',(milli,initials.strip()[:8],note.strip()[:250],line_id)); audit(user['id'],'pack','order_line',line_id,f'packed={packed_qty}'); flash(request,'Packed quantity saved.','success')
        except Exception as e: flash(request,str(e),'error')
    return RedirectResponse(f"/packing/round/{row['round_id'] if row else ''}",303)
