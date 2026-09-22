from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from ..dependencies import require_role
from ..constants import ROLE_MEMBER
from ..db import all_rows, one
from ..security import valid_csrf
from ..services.order_service import current_open_round,products_for_round,member_order,order_lines,save_member_order,cancel_order,order_total,OrderError
from ..services.audit_service import audit
from ..services.pricing import milli_to_quantity
from ..web import render,flash,pop_flash

router=APIRouter(prefix='/member')

@router.get('')
def dashboard(request: Request):
    user=require_role(request,ROLE_MEMBER); rnd=current_open_round(); order=member_order(rnd['id'],user['id']) if rnd else None
    history=all_rows('''SELECT o.*,r.number,r.status round_status,r.pickup_at FROM orders o JOIN rounds r ON r.id=o.round_id
                        WHERE o.user_id=? ORDER BY r.number DESC LIMIT 8''',(user['id'],))
    return render(request,'member/dashboard.html',round=rnd,order=order,history=history,flash=pop_flash(request),order_total=order_total(order['id']) if order and order['status']!='cancelled' else 0)

@router.get('/products')
def products(request: Request):
    require_role(request,ROLE_MEMBER); rnd=current_open_round(); items=products_for_round(rnd['id']) if rnd else []
    return render(request,'member/products.html',round=rnd,products=items,flash=pop_flash(request))

@router.get('/order')
def edit_order(request: Request):
    user=require_role(request,ROLE_MEMBER); rnd=current_open_round()
    if not rnd: return render(request,'member/order_edit.html',round=None,products=[],existing={})
    order=member_order(rnd['id'],user['id']); existing={}
    if order and order['status']!='cancelled':
        existing={x['round_product_id']:milli_to_quantity(x['requested_milli'],x['sale_type']) for x in order_lines(order['id'])}
    return render(request,'member/order_edit.html',round=rnd,products=products_for_round(rnd['id']),order=order,existing=existing,flash=pop_flash(request))

@router.post('/order')
async def save_order(request: Request):
    user=require_role(request,ROLE_MEMBER); form=await request.form()
    if not valid_csrf(request.session,form.get('csrf_token')): return RedirectResponse('/member/order',303)
    rnd=current_open_round()
    if not rnd: flash(request,'There is no open round.','error'); return RedirectResponse('/member/order',303)
    quantities={}
    for key,value in form.items():
        if key.startswith('qty_'):
            try: quantities[int(key[4:])]=value
            except ValueError: pass
    try:
        oid=save_member_order(rnd['id'],user['id'],quantities); audit(user['id'],'save','order',oid,f'Round {rnd["number"]}')
        flash(request,'Your order has been saved.','success')
    except OrderError as e: flash(request,str(e),'error')
    return RedirectResponse('/member/order',303)

@router.post('/order/{order_id}/cancel')
def cancel(request: Request, order_id:int, csrf_token:str=Form(...)):
    user=require_role(request,ROLE_MEMBER)
    if valid_csrf(request.session,csrf_token):
        try: cancel_order(order_id,user['id']); audit(user['id'],'cancel','order',order_id); flash(request,'Order cancelled.','success')
        except OrderError as e: flash(request,str(e),'error')
    return RedirectResponse('/member',303)

@router.get('/orders/{order_id}')
def order_detail(request: Request, order_id:int):
    user=require_role(request,ROLE_MEMBER)
    order=one('''SELECT o.*,r.number,r.status round_status,r.pickup_at FROM orders o JOIN rounds r ON r.id=o.round_id
                 WHERE o.id=? AND o.user_id=?''',(order_id,user['id']))
    if not order: return RedirectResponse('/member',303)
    return render(request,'member/order_detail.html',order=order,lines=order_lines(order_id),total=order_total(order_id),flash=pop_flash(request))
