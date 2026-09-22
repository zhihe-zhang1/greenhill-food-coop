from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from ..db import one
from ..security import verify_password, valid_csrf
from ..web import render, flash

router=APIRouter()

@router.get('/login')
def login_page(request: Request):
    if request.session.get('user_id'): return RedirectResponse('/',303)
    return render(request,'login.html')

@router.post('/login')
def login(request: Request, email: str=Form(...), password: str=Form(...), csrf_token: str=Form(...)):
    if not valid_csrf(request.session,csrf_token): return render(request,'login.html',error='Session expired. Refresh and try again.'),403
    user=one('SELECT * FROM users WHERE lower(email)=lower(?) AND active=1',(email.strip(),))
    if not user or not verify_password(password,user['password_hash']):
        return render(request,'login.html',error='Invalid email or password.')
    request.session.clear(); request.session['user_id']=user['id']; flash(request,f"Welcome back, {user['name']}!",'success')
    return RedirectResponse('/',303)

@router.post('/logout')
def logout(request: Request, csrf_token: str=Form(...)):
    if valid_csrf(request.session,csrf_token): request.session.clear()
    return RedirectResponse('/login',303)
