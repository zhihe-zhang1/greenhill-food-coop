def login(client,email,password):
    r=client.get('/login'); token=r.text.split('name="csrf_token" value="',1)[1].split('"',1)[0]
    return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=True)

def test_totals_api_requires_authorized_role(client):
    from app.db import one
    rid=one('SELECT id FROM rounds ORDER BY number DESC LIMIT 1')['id']
    r=client.get(f'/api/rounds/{rid}/totals'); assert r.status_code==401
    login(client,'coordinator@greenhill.local','Coordinator123!')
    r=client.get(f'/api/rounds/{rid}/totals'); assert r.status_code==200; assert 'products' in r.json()
