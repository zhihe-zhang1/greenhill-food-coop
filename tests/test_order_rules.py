from app.db import one,execute
from app.services.order_service import current_open_round,products_for_round,save_member_order,member_order,order_total,OrderError

def test_member_order_saves_and_prices():
    rnd=current_open_round(); user=one("SELECT * FROM users WHERE email='member@greenhill.local'")
    products=products_for_round(rnd['id']); oats=next(p for p in products if p['name'].startswith('Rolled oats')); eggs=next(p for p in products if p['name'].startswith('Eggs'))
    oid=save_member_order(rnd['id'],user['id'],{oats['round_product_id']:'1.5',eggs['round_product_id']:'2'})
    assert member_order(rnd['id'],user['id'])['id']==oid
    assert order_total(oid)==510+1500

def test_closed_round_rejects_edit():
    rnd=current_open_round(); user=one("SELECT * FROM users WHERE email='member@greenhill.local'")
    execute("UPDATE rounds SET status='closed' WHERE id=?",(rnd['id'],))
    try:
        try: save_member_order(rnd['id'],user['id'],{})
        except OrderError: pass
        else: raise AssertionError('Expected OrderError')
    finally: execute("UPDATE rounds SET status='open' WHERE id=?",(rnd['id'],))
