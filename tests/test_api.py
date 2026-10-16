"""Access-controlled totals API tests - member C scope (GHC-A3-12).

The API is the integration point between the member order flow, the coordinator
report and the packing team, so the tests cover the access rules, the payload
contract and the price-snapshot rule.
"""
from app.db import one, execute
from app.services.order_service import cancel_order

COORDINATOR=('coordinator@greenhill.local','Coordinator123!')
PACKER=('packer@greenhill.local','Packer123!')
MEMBER=('member@greenhill.local','Member123!')
MEMBER_2=('jan@example.local','Member123!')

KG_PRODUCT='Rolled oats, organic'          # 340 cents per kg in the demo seed


def login(client,email,password):
    r=client.get('/login'); token=r.text.split('name="csrf_token" value="',1)[1].split('"',1)[0]
    return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=True)


def totals(client,rid): return client.get(f'/api/rounds/{rid}/totals')


def product_entry(payload,name):
    return next(x for x in payload['products'] if x['name']==name)


def test_totals_api_requires_authorized_role(client):
    rid=one('SELECT id FROM rounds ORDER BY number DESC LIMIT 1')['id']
    r=client.get(f'/api/rounds/{rid}/totals'); assert r.status_code==401
    login(client,'coordinator@greenhill.local','Coordinator123!')
    r=client.get(f'/api/rounds/{rid}/totals'); assert r.status_code==200; assert 'products' in r.json()


def test_totals_api_rejects_anonymous_and_member(client, login):
    assert totals(client,1).status_code==401
    login(*MEMBER)
    assert totals(client,1).status_code==403


def test_totals_api_is_available_to_the_packing_team(client, login):
    """The packing team needs the consolidated quantities to check the bulk order."""
    login(*PACKER)
    r=totals(client,one('SELECT id FROM rounds ORDER BY number DESC LIMIT 1')['id'])
    assert r.status_code==200


def test_totals_api_payload_contract(client, login, new_round, place_order):
    rid=new_round()
    place_order(rid,MEMBER[0],KG_PRODUCT,'2.5')
    login(*COORDINATOR)
    payload=totals(client,rid).json()
    assert payload['round']['number'] is not None
    entry=product_entry(payload,KG_PRODUCT)
    assert entry['sale_type']=='kg'
    assert entry['quantity']=='2.5'
    # 2.5 kg at 340 cents per kg
    assert entry['total']=='$8.50'
    assert entry['requested_milli']==2500 and entry['order_count']==1


def test_totals_api_for_an_unknown_round_returns_an_empty_payload(client, login):
    login(*COORDINATOR)
    payload=totals(client,999999).json()
    assert payload=={'round':None,'products':[]}


def test_totals_api_excludes_cancelled_orders(client, login, new_round, place_order):
    rid=new_round()
    place_order(rid,MEMBER[0],KG_PRODUCT,'2')
    cancelled,_=place_order(rid,MEMBER_2[0],KG_PRODUCT,'1')
    cancel_order(cancelled,one('SELECT id FROM users WHERE email=?',(MEMBER_2[0],))['id'])
    login(*COORDINATOR)
    entry=product_entry(totals(client,rid).json(),KG_PRODUCT)
    assert entry['quantity']=='2' and entry['total']=='$6.80' and entry['order_count']==1


def test_totals_api_uses_the_round_price_snapshot_when_a_product_price_changes(client, login, new_round, place_order):
    """A later product price change applies to future rounds only."""
    rid=new_round()
    place_order(rid,MEMBER[0],KG_PRODUCT,'2')
    login(*COORDINATOR)
    before=product_entry(totals(client,rid).json(),KG_PRODUCT)
    execute('UPDATE products SET price_cents=price_cents+100 WHERE name=?',(KG_PRODUCT,))
    after=product_entry(totals(client,rid).json(),KG_PRODUCT)
    assert after['total']==before['total']=='$6.80'
    execute('UPDATE products SET price_cents=price_cents-100 WHERE name=?',(KG_PRODUCT,))


def test_health_endpoint_stays_public(client):
    assert client.get('/api/health').json()=={'status':'ok'}
