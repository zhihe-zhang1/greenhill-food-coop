from fastapi import APIRouter,Request,Form,HTTPException
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

LINE_SQL='''SELECT ol.*,o.round_id,o.status order_status,p.sale_type
            FROM order_lines ol
            JOIN round_products rp ON rp.id=ol.round_product_id
            JOIN products p ON p.id=rp.product_id
            JOIN orders o ON o.id=ol.order_id
            WHERE ol.id=?'''

@router.get('/round/{rid}')
def sheet(request:Request,rid:int):
    guard(request); rnd=one('SELECT * FROM rounds WHERE id=?',(rid,))
    if not rnd: raise HTTPException(404,'Round not found.')
    return render(request,'packing/sheet.html',round=rnd,rows=packing_rows(rid),flash=pop_flash(request))

@router.post('/line/{line_id}')
def update_line(request:Request,line_id:int,packed_qty:str=Form(...),initials:str=Form(''),note:str=Form(''),csrf_token:str=Form(...)):
    user=guard(request); row=one(LINE_SQL,(line_id,))
    if not row: raise HTTPException(404,'Order line not found.')
    back=RedirectResponse(f"/packing/round/{row['round_id']}",303)
    if not valid_csrf(request.session,csrf_token):
        flash(request,'Session expired. Refresh the packing sheet and try again.','error'); return back
    # A cancelled order is excluded from the packing sheet, the round totals and the CSV
    # export, so its lines must not accept packed quantities either (DEF-006).
    if row['order_status']=='cancelled':
        flash(request,'This order was cancelled, so its lines cannot be packed.','error'); return back
    try:
        milli=quantity_to_milli(packed_qty,row['sale_type'])
    except (ValueError,ArithmeticError) as e:
        flash(request,str(e),'error'); return back
    # A blank or zero entry must not be stored: packing completion counts lines where
    # packed_milli IS NOT NULL, so writing 0 would report an unpacked line as packed (DEF-007).
    if milli<=0:
        flash(request,'Enter a packed quantity greater than zero.','error'); return back
    execute('UPDATE order_lines SET packed_milli=?,packer_initials=?,note=? WHERE id=?',
            (milli,initials.strip()[:8],note.strip()[:250],line_id))
    audit(user['id'],'pack','order_line',line_id,f'packed={packed_qty}')
    flash(request,'Packed quantity saved.','success')
    return back
