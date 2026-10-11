def login(client,email,password):
    r=client.get('/login'); token=r.text.split('name="csrf_token" value="',1)[1].split('"',1)[0]
    return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=True)

def test_packing_sheet_can_record_actual_quantity(client):
    from app.db import one
    from app.services.order_service import save_member_order
    rnd=one("SELECT * FROM rounds WHERE status='open' ORDER BY number DESC LIMIT 1")
    user=one("SELECT * FROM users WHERE email='member@greenhill.local'")
    rp=one('SELECT rp.id,p.sale_type FROM round_products rp JOIN products p ON p.id=rp.product_id WHERE rp.round_id=? ORDER BY rp.id LIMIT 1',(rnd['id'],))
    oid=save_member_order(rnd['id'],user['id'],{rp['id']:'1'})
    line=one('SELECT id FROM order_lines WHERE order_id=?',(oid,))
    login(client,'packer@greenhill.local','Packer123!')
    page=client.get(f"/packing/round/{rnd['id']}"); assert page.status_code==200
    token=page.text.split('name="csrf_token" value="',1)[1].split('"',1)[0]
    r=client.post(f"/packing/line/{line['id']}",data={'packed_qty':'1','initials':'BN','note':'checked','csrf_token':token},follow_redirects=True)
    assert r.status_code==200
    saved=one('SELECT packed_milli,packer_initials,note FROM order_lines WHERE id=?',(line['id'],))
    assert saved['packed_milli'] is not None and saved['packer_initials']=='BN' and saved['note']=='checked'
