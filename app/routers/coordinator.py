from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from ..dependencies import require_role
from ..constants import ROLE_COORDINATOR
from ..db import all_rows,one,execute,connect
from ..security import valid_csrf,hash_password
from ..services.audit_service import audit
from ..services.order_service import order_total
from ..services.reporting_service import round_totals
from ..web import render,flash,pop_flash

router=APIRouter(prefix='/coordinator')

def guard(request): return require_role(request,ROLE_COORDINATOR)

@router.get('')
def dashboard(request:Request):
    user=guard(request)
    stats={
      'members':one("SELECT COUNT(*) n FROM users WHERE role='member' AND active=1")['n'],
      'products':one('SELECT COUNT(*) n FROM products WHERE active=1')['n'],
      'orders':one("SELECT COUNT(*) n FROM orders WHERE status='submitted'")['n'],
      'rounds':one('SELECT COUNT(*) n FROM rounds')['n']}
    rounds=all_rows('SELECT * FROM rounds ORDER BY number DESC LIMIT 5')
    return render(request,'coordinator/dashboard.html',stats=stats,rounds=rounds,flash=pop_flash(request))

@router.get('/products')
def products(request:Request):
    guard(request); return render(request,'coordinator/products.html',products=all_rows('SELECT * FROM products ORDER BY active DESC,name'),flash=pop_flash(request))

@router.get('/products/new')
def product_new(request:Request): guard(request); return render(request,'coordinator/product_form.html',product=None)

@router.get('/products/{pid}/edit')
def product_edit(request:Request,pid:int): guard(request); return render(request,'coordinator/product_form.html',product=one('SELECT * FROM products WHERE id=?',(pid,)))

@router.post('/products/save')
def product_save(request:Request,csrf_token:str=Form(...),id:str=Form(''),name:str=Form(...),description:str=Form(''),sale_type:str=Form(...),price:str=Form(...),bay:str=Form(''),active:str=Form('1')):
    user=guard(request)
    if not valid_csrf(request.session,csrf_token): return RedirectResponse('/coordinator/products',303)
    try: cents=int(round(float(price)*100)); assert sale_type in ('unit','kg') and cents>=0
    except Exception: flash(request,'Invalid price or sale type.','error'); return RedirectResponse('/coordinator/products',303)
    if id:
        execute('UPDATE products SET name=?,description=?,sale_type=?,price_cents=?,bay=?,active=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(name.strip(),description.strip(),sale_type,cents,bay.strip(),1 if active=='1' else 0,int(id))); pid=int(id); action='update'
    else:
        pid=execute('INSERT INTO products(name,description,sale_type,price_cents,bay,active) VALUES(?,?,?,?,?,?)',(name.strip(),description.strip(),sale_type,cents,bay.strip(),1 if active=='1' else 0)); action='create'
    audit(user['id'],action,'product',pid,name); flash(request,'Product saved. Future rounds will use the new base price.','success')
    return RedirectResponse('/coordinator/products',303)

@router.post('/products/{pid}/toggle')
def product_toggle(request:Request,pid:int,csrf_token:str=Form(...)):
    user=guard(request)
    if valid_csrf(request.session,csrf_token): execute('UPDATE products SET active=1-active,updated_at=CURRENT_TIMESTAMP WHERE id=?',(pid,)); audit(user['id'],'toggle','product',pid); flash(request,'Product availability updated.','success')
    return RedirectResponse('/coordinator/products',303)

@router.get('/members')
def members(request:Request): guard(request); return render(request,'coordinator/members.html',members=all_rows("SELECT * FROM users WHERE role='member' ORDER BY active DESC,member_no"),flash=pop_flash(request))

@router.get('/members/new')
def member_new(request:Request): guard(request); return render(request,'coordinator/member_form.html',member=None)

@router.get('/members/{uid}/edit')
def member_edit(request:Request,uid:int): guard(request); return render(request,'coordinator/member_form.html',member=one("SELECT * FROM users WHERE id=? AND role='member'",(uid,)))

@router.post('/members/save')
def member_save(request:Request,csrf_token:str=Form(...),id:str=Form(''),member_no:str=Form(...),name:str=Form(...),email:str=Form(...),phone:str=Form(''),address:str=Form(''),crate_no:str=Form(''),active:str=Form('1'),password:str=Form('')):
    user=guard(request)
    if not valid_csrf(request.session,csrf_token): return RedirectResponse('/coordinator/members',303)
    crate=int(crate_no) if crate_no.strip().isdigit() else None
    try:
        if id:
            if password.strip(): execute('UPDATE users SET member_no=?,name=?,email=?,phone=?,address=?,crate_no=?,active=?,password_hash=? WHERE id=?',(member_no,name,email,phone,address,crate,1 if active=='1' else 0,hash_password(password),int(id)))
            else: execute('UPDATE users SET member_no=?,name=?,email=?,phone=?,address=?,crate_no=?,active=? WHERE id=?',(member_no,name,email,phone,address,crate,1 if active=='1' else 0,int(id)))
            uid=int(id); action='update'
        else:
            uid=execute("INSERT INTO users(member_no,name,email,phone,address,crate_no,role,active,password_hash) VALUES(?,?,?,?,?,?,'member',?,?)",(member_no,name,email,phone,address,crate,1 if active=='1' else 0,hash_password(password or 'Member123!'))); action='create'
        audit(user['id'],action,'member',uid,name); flash(request,'Member saved.','success')
    except Exception as e: flash(request,f'Could not save member: {e}','error')
    return RedirectResponse('/coordinator/members',303)

@router.get('/rounds')
def rounds(request:Request): guard(request); return render(request,'coordinator/rounds.html',rounds=all_rows('SELECT * FROM rounds ORDER BY number DESC'),flash=pop_flash(request))

@router.post('/rounds/new')
def round_new(request:Request,csrf_token:str=Form(...),number:int=Form(...),opens_at:str=Form(...),closes_at:str=Form(...),pickup_at:str=Form(...)):
    user=guard(request)
    if not valid_csrf(request.session,csrf_token): return RedirectResponse('/coordinator/rounds',303)
    try:
        with connect() as con:
            rid=con.execute("INSERT INTO rounds(number,opens_at,closes_at,pickup_at,status) VALUES(?,?,?,?,'open')",(number,opens_at,closes_at,pickup_at)).lastrowid
            con.execute('INSERT INTO round_products(round_id,product_id,price_cents,available) SELECT ?,id,price_cents,active FROM products',(rid,))
        audit(user['id'],'create','round',rid,f'Round {number}'); flash(request,'Round created and current product prices were snapshotted.','success')
    except Exception as e: flash(request,f'Could not create round: {e}','error')
    return RedirectResponse('/coordinator/rounds',303)

@router.post('/rounds/{rid}/status')
def round_status(request:Request,rid:int,status:str=Form(...),csrf_token:str=Form(...)):
    user=guard(request)
    if valid_csrf(request.session,csrf_token) and status in ('open','closed','packed'):
        execute('UPDATE rounds SET status=? WHERE id=?',(status,rid)); audit(user['id'],'status','round',rid,status); flash(request,f'Round status changed to {status}.','success')
    return RedirectResponse('/coordinator/rounds',303)

@router.get('/rounds/{rid}/orders')
def round_orders(request:Request,rid:int):
    guard(request); rnd=one('SELECT * FROM rounds WHERE id=?',(rid,)); orders=all_rows('''SELECT o.*,u.member_no,u.name,u.crate_no FROM orders o JOIN users u ON u.id=o.user_id WHERE o.round_id=? ORDER BY u.crate_no,u.name''',(rid,))
    enriched=[dict(o,total_cents=order_total(o['id'])) for o in orders]
    return render(request,'coordinator/orders.html',round=rnd,orders=enriched,flash=pop_flash(request))

@router.get('/rounds/{rid}/totals')
def totals(request:Request,rid:int):
    guard(request); return render(request,'coordinator/round_totals.html',round=one('SELECT * FROM rounds WHERE id=?',(rid,)),totals=round_totals(rid),flash=pop_flash(request))

@router.get('/audit')
def audit_page(request:Request):
    guard(request); rows=all_rows('''SELECT a.*,u.name user_name FROM audit_log a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT 200''')
    return render(request,'coordinator/audit.html',rows=rows)
