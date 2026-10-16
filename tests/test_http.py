"""HTTP routing, session and error-page tests - member C scope (GHC-A3-12).

These tests cover the contract the whole application depends on: who may reach
each landing page, how the login form behaves on bad input, that logging out
really clears the session, and that unknown URLs render the error page instead of
a stack trace.
"""
MEMBER=('member@greenhill.local','Member123!')
COORDINATOR=('coordinator@greenhill.local','Coordinator123!')
PACKER=('packer@greenhill.local','Packer123!')


def _login(client,email,password):
    r=client.get('/login'); token=r.text.split('name="csrf_token" value="',1)[1].split('"',1)[0]
    return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=True)


def test_login_page(client): assert client.get('/login').status_code==200

def test_member_can_login(client):
    r=_login(client,'member@greenhill.local','Member123!'); assert r.status_code==200; assert 'Hello' in r.text

def test_health(client): assert client.get('/api/health').json()=={'status':'ok'}


def test_login_rejects_a_wrong_password(client):
    r=_login(client,'member@greenhill.local','not-the-password')
    assert r.status_code==200
    assert 'Invalid email or password' in r.text
    assert client.get('/member',follow_redirects=False).status_code==401


def test_login_rejects_a_forged_csrf_token(client):
    client.get('/login')
    r=client.post('/login',data={'email':'member@greenhill.local','password':'Member123!','csrf_token':'forged'})
    assert r.status_code==403
    assert 'Session expired' in r.text


def test_anonymous_visitor_is_redirected_to_the_login_page(client):
    r=client.get('/',follow_redirects=False)
    assert r.status_code==303 and r.headers['location']=='/login'


def test_each_role_lands_on_its_own_home_page(client, login):
    login(*MEMBER); r=client.get('/',follow_redirects=False)
    assert r.status_code==303 and r.headers['location']=='/member'
    login(*COORDINATOR); r=client.get('/',follow_redirects=False)
    assert r.status_code==303 and r.headers['location']=='/coordinator'
    login(*PACKER); r=client.get('/',follow_redirects=False)
    assert r.status_code==200 and 'Packing workspace' in r.text


def test_logout_clears_the_session(client, login, logout):
    login(*MEMBER)
    assert client.get('/member',follow_redirects=False).status_code==200
    logout()
    assert client.get('/member',follow_redirects=False).status_code==401


def test_unknown_url_renders_the_404_page(client, login):
    login(*MEMBER)
    r=client.get('/definitely-not-a-route')
    assert r.status_code==404
