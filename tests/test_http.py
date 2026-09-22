def _login(client,email,password):
    r=client.get('/login'); token=r.text.split('name="csrf_token" value="',1)[1].split('"',1)[0]
    return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=True)

def test_login_page(client): assert client.get('/login').status_code==200

def test_member_can_login(client):
    r=_login(client,'member@greenhill.local','Member123!'); assert r.status_code==200; assert 'Hello' in r.text

def test_health(client): assert client.get('/api/health').json()=={'status':'ok'}
