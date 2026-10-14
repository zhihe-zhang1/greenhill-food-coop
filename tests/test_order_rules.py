"""Order lifecycle rules: snapshot pricing, edits, cancellation and access limits.

Story: MSD426GXUST34-9
"""
import pytest

from app.db import one,execute
from app.services.order_service import (
    current_open_round,products_for_round,save_member_order,member_order,order_total,
    cancel_order,order_lines,OrderError)

MEMBER_EMAIL='member@greenhill.local'
OTHER_MEMBER_EMAIL='jan@example.local'


def _member(email=MEMBER_EMAIL):
    return one('SELECT * FROM users WHERE email=?',(email,))


def _product(round_id, prefix):
    return next(p for p in products_for_round(round_id) if p['name'].startswith(prefix))


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


def test_order_prices_from_the_round_snapshot_not_the_live_catalogue():
    """Acceptance criterion: members settle at the round's frozen unit price."""
    rnd=current_open_round(); user=_member()
    oats=_product(rnd['id'],'Rolled oats'); snapshot_cents=oats['price_cents']
    oid=save_member_order(rnd['id'],user['id'],{oats['round_product_id']:'2'})
    assert order_total(oid)==snapshot_cents*2
    live_before=one('SELECT price_cents FROM products WHERE name=?',(oats['name'],))['price_cents']
    execute('UPDATE products SET price_cents=? WHERE name=?',(live_before+5000,oats['name']))
    try:
        # the live catalogue changed, but the round snapshot must still drive the total
        assert order_total(oid)==snapshot_cents*2
    finally:
        execute('UPDATE products SET price_cents=? WHERE name=?',(live_before,oats['name']))


def test_editing_an_order_replaces_its_lines():
    rnd=current_open_round(); user=_member()
    oats=_product(rnd['id'],'Rolled oats'); eggs=_product(rnd['id'],'Eggs')
    oid=save_member_order(rnd['id'],user['id'],{oats['round_product_id']:'1',eggs['round_product_id']:'1'})
    assert len(order_lines(oid))==2
    save_member_order(rnd['id'],user['id'],{oats['round_product_id']:'3'})
    lines=order_lines(oid)
    assert len(lines)==1 and lines[0]['name'].startswith('Rolled oats')
    assert order_total(oid)==oats['price_cents']*3


def test_empty_or_all_zero_order_is_rejected():
    rnd=current_open_round(); user=_member()
    with pytest.raises(OrderError): save_member_order(rnd['id'],user['id'],{})
    oats=_product(rnd['id'],'Rolled oats')
    with pytest.raises(OrderError): save_member_order(rnd['id'],user['id'],{oats['round_product_id']:'0'})


def test_member_can_cancel_their_own_order_in_an_open_round():
    rnd=current_open_round(); user=_member()
    oats=_product(rnd['id'],'Rolled oats')
    oid=save_member_order(rnd['id'],user['id'],{oats['round_product_id']:'1'})
    cancel_order(oid,user['id'])
    assert one('SELECT status FROM orders WHERE id=?',(oid,))['status']=='cancelled'


def test_member_cannot_cancel_another_members_order():
    rnd=current_open_round()
    owner=_member(); intruder=_member(OTHER_MEMBER_EMAIL)
    oats=_product(rnd['id'],'Rolled oats')
    oid=save_member_order(rnd['id'],owner['id'],{oats['round_product_id']:'1'})
    with pytest.raises(OrderError): cancel_order(oid,intruder['id'])


def test_closed_round_blocks_cancellation():
    rnd=current_open_round(); user=_member()
    oats=_product(rnd['id'],'Rolled oats')
    oid=save_member_order(rnd['id'],user['id'],{oats['round_product_id']:'1'})
    execute("UPDATE rounds SET status='closed' WHERE id=?",(rnd['id'],))
    try:
        with pytest.raises(OrderError): cancel_order(oid,user['id'])
        assert one('SELECT status FROM orders WHERE id=?',(oid,))['status']=='submitted'
    finally:
        execute("UPDATE rounds SET status='open' WHERE id=?",(rnd['id'],))
