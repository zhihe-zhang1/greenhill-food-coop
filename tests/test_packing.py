"""Packing flow tests - member C scope (GHC-A3-11).

Covers the happy path, the packing rules that protect the round totals, and the
negative paths that keep cancelled orders, invalid input and forged POSTs out of
the packing data.
"""
from datetime import datetime, timedelta

from app.db import one, all_rows, execute
from app.services.order_service import save_member_order, cancel_order

PACKER=('packer@greenhill.local','Packer123!')
MEMBER=('member@greenhill.local','Member123!')
MEMBER_2=('jan@example.local','Member123!')

KG_PRODUCT='Rolled oats, organic'
UNIT_PRODUCT='Tahini, 375 g jar'


def login(client,email,password):
    r=client.get('/login'); token=csrf_from(r.text)
    return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=True)


def csrf_from(text):
    return text.split('name="csrf_token" value="',1)[1].split('"',1)[0]


def make_round(number):
    """Create an isolated open round so each test owns its own data."""
    now=datetime.now().replace(microsecond=0)
    rid=execute('INSERT INTO rounds(number,opens_at,closes_at,pickup_at,status) VALUES(?,?,?,?,?)',
                (number,(now-timedelta(days=1)).isoformat(' '),(now+timedelta(days=6)).isoformat(' '),
                 (now+timedelta(days=9)).isoformat(' '),'open'))
    execute('INSERT INTO round_products(round_id,product_id,price_cents,available) SELECT ?,id,price_cents,active FROM products',(rid,))
    return rid


def place_order(round_id,member_email,product_name,quantity='1'):
    user=one('SELECT * FROM users WHERE email=?',(member_email,))
    rp=one('''SELECT rp.id FROM round_products rp JOIN products p ON p.id=rp.product_id
              WHERE rp.round_id=? AND p.name=?''',(round_id,product_name))
    oid=save_member_order(round_id,user['id'],{rp['id']:quantity})
    return oid,one('SELECT * FROM order_lines WHERE order_id=?',(oid,))


def sheet_token(client,round_id):
    page=client.get(f'/packing/round/{round_id}')
    assert page.status_code==200
    return csrf_from(page.text)


def test_packing_sheet_can_record_actual_quantity(client):
    rnd=one("SELECT * FROM rounds WHERE status='open' ORDER BY number DESC LIMIT 1")
    user=one("SELECT * FROM users WHERE email='member@greenhill.local'")
    rp=one('SELECT rp.id,p.sale_type FROM round_products rp JOIN products p ON p.id=rp.product_id WHERE rp.round_id=? ORDER BY rp.id LIMIT 1',(rnd['id'],))
    oid=save_member_order(rnd['id'],user['id'],{rp['id']:'1'})
    line=one('SELECT id FROM order_lines WHERE order_id=?',(oid,))
    login(client,'packer@greenhill.local','Packer123!')
    page=client.get(f"/packing/round/{rnd['id']}"); assert page.status_code==200
    token=csrf_from(page.text)
    r=client.post(f"/packing/line/{line['id']}",data={'packed_qty':'1','initials':'BN','note':'checked','csrf_token':token},follow_redirects=True)
    assert r.status_code==200
    saved=one('SELECT packed_milli,packer_initials,note FROM order_lines WHERE id=?',(line['id'],))
    assert saved['packed_milli'] is not None and saved['packer_initials']=='BN' and saved['note']=='checked'


def test_packing_sheet_requires_a_packing_or_coordinator_role(client):
    rnd=make_round(901)
    assert client.get(f'/packing/round/{rnd}').status_code==401
    login(client,*MEMBER)
    assert client.get(f'/packing/round/{rnd}').status_code==403
    login(client,*PACKER)
    assert client.get(f'/packing/round/{rnd}').status_code==200


def test_unknown_round_returns_not_found(client):
    login(client,*PACKER)
    assert client.get('/packing/round/999999').status_code==404


def test_packer_records_a_short_packed_weight_for_a_kg_product(client):
    rnd=make_round(902); oid,line=place_order(rnd,MEMBER[0],KG_PRODUCT,'3')
    login(client,*PACKER); token=sheet_token(client,rnd)
    r=client.post(f"/packing/line/{line['id']}",data={'packed_qty':'2.475','initials':'x','note':'short supply','csrf_token':token},follow_redirects=True)
    assert r.status_code==200
    saved=one('SELECT packed_milli,note FROM order_lines WHERE id=?',(line['id'],))
    assert saved['packed_milli']==2475 and saved['note']=='short supply'
    assert 'short supply' in client.get(f'/packing/round/{rnd}').text


def test_fractional_quantity_is_rejected_for_a_unit_product(client):
    rnd=make_round(903); oid,line=place_order(rnd,MEMBER[0],UNIT_PRODUCT,'2')
    login(client,*PACKER); token=sheet_token(client,rnd)
    client.post(f"/packing/line/{line['id']}",data={'packed_qty':'1.5','initials':'BN','csrf_token':token},follow_redirects=True)
    assert one('SELECT packed_milli FROM order_lines WHERE id=?',(line['id'],))['packed_milli'] is None


def test_non_numeric_quantity_is_reported_instead_of_failing(client):
    rnd=make_round(904); oid,line=place_order(rnd,MEMBER[0],KG_PRODUCT,'1')
    login(client,*PACKER); token=sheet_token(client,rnd)
    r=client.post(f"/packing/line/{line['id']}",data={'packed_qty':'two kilos','initials':'BN','csrf_token':token},follow_redirects=True)
    assert r.status_code==200
    assert 'Quantity must be a number' in r.text
    assert one('SELECT packed_milli FROM order_lines WHERE id=?',(line['id'],))['packed_milli'] is None


def test_blank_or_zero_quantity_is_not_recorded_as_packed(client):
    """DEF-007: packing completion counts lines where packed_milli IS NOT NULL."""
    rnd=make_round(905); oid,line=place_order(rnd,MEMBER[0],UNIT_PRODUCT,'1')
    login(client,*PACKER); token=sheet_token(client,rnd)
    for raw in ('','0','   '):
        client.post(f"/packing/line/{line['id']}",data={'packed_qty':raw,'initials':'BN','csrf_token':token},follow_redirects=True)
        assert one('SELECT packed_milli FROM order_lines WHERE id=?',(line['id'],))['packed_milli'] is None


def test_cancelled_order_lines_cannot_be_packed(client):
    """DEF-006: a cancelled order is excluded from the sheet, totals and CSV."""
    rnd=make_round(906)
    oid,line=place_order(rnd,MEMBER[0],KG_PRODUCT,'2')
    cancel_order(oid,one('SELECT id FROM users WHERE email=?',(MEMBER[0],))['id'])
    assert one('SELECT packed_milli FROM order_lines WHERE id=?',(line['id'],))['packed_milli'] is None
    login(client,*PACKER); token=sheet_token(client,rnd)
    r=client.post(f"/packing/line/{line['id']}",data={'packed_qty':'2','initials':'BN','csrf_token':token},follow_redirects=True)
    assert 'cannot be packed' in r.text
    assert one('SELECT packed_milli FROM order_lines WHERE id=?',(line['id'],))['packed_milli'] is None


def test_cancelled_order_is_not_listed_on_the_packing_sheet(client):
    rnd=make_round(907)
    keep_oid,keep_line=place_order(rnd,MEMBER[0],KG_PRODUCT,'1')
    cancel_oid,cancel_line=place_order(rnd,MEMBER_2[0],KG_PRODUCT,'1')
    cancel_order(cancel_oid,one('SELECT id FROM users WHERE email=?',(MEMBER_2[0],))['id'])
    login(client,*PACKER); page=client.get(f'/packing/round/{rnd}')
    assert f'/packing/line/{keep_line["id"]}' in page.text
    assert f'/packing/line/{cancel_line["id"]}' not in page.text


def test_forged_csrf_token_cannot_change_packed_quantity(client):
    """DEF-008: a rejected POST must be distinguishable from a saved one."""
    rnd=make_round(908); oid,line=place_order(rnd,MEMBER[0],KG_PRODUCT,'1')
    login(client,*PACKER)
    r=client.post(f"/packing/line/{line['id']}",data={'packed_qty':'1','initials':'BN','csrf_token':'not-a-token'},follow_redirects=True)
    assert 'Session expired' in r.text
    assert one('SELECT packed_milli FROM order_lines WHERE id=?',(line['id'],))['packed_milli'] is None


def test_unknown_line_returns_not_found_instead_of_a_broken_redirect(client):
    """DEF-008: an unknown line id used to redirect to the malformed URL /packing/round/."""
    rnd=make_round(909); login(client,*PACKER); token=sheet_token(client,rnd)
    r=client.post('/packing/line/999999',data={'packed_qty':'1','initials':'BN','csrf_token':token},follow_redirects=False)
    assert r.status_code==404


def test_successful_pack_is_audited_and_printed_on_the_sheet(client):
    rnd=make_round(910); oid,line=place_order(rnd,MEMBER[0],KG_PRODUCT,'2')
    login(client,*PACKER); token=sheet_token(client,rnd)
    client.post(f"/packing/line/{line['id']}",data={'packed_qty':'2','initials':'CT','note':'ok','csrf_token':token},follow_redirects=True)
    entry=one("SELECT * FROM audit_log WHERE entity_type='order_line' AND entity_id=? ORDER BY id DESC LIMIT 1",(line['id'],))
    assert entry and entry['action']=='pack' and entry['detail']=='packed=2'
    page=client.get(f'/packing/round/{rnd}')
    assert 'CT' in page.text
