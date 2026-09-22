from fastapi import Request, HTTPException
from .db import one

def current_user(request: Request):
    uid=request.session.get('user_id')
    return one('SELECT * FROM users WHERE id=? AND active=1',(uid,)) if uid else None

def require_user(request: Request):
    user=current_user(request)
    if not user: raise HTTPException(401,'Login required')
    return user

def require_role(request: Request, *roles):
    user=require_user(request)
    if user['role'] not in roles: raise HTTPException(403,'You do not have permission to access this page.')
    return user
