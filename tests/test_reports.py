def login(client,email,password):
    r=client.get('/login'); token=r.text.split('name="csrf_token" value="',1)[1].split('"',1)[0]
    return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=True)

def test_coordinator_round_report_and_csv(client):
    login(client,'coordinator@greenhill.local','Coordinator123!')
    from app.db import one
    rid=one('SELECT id FROM rounds ORDER BY number DESC LIMIT 1')['id']
    r=client.get(f'/reports/round/{rid}'); assert r.status_code==200; assert 'Round #' in r.text
    csv=client.get(f'/reports/round/{rid}/csv'); assert csv.status_code==200; assert 'Member No' in csv.text

def test_release_readiness(client):
    login(client,'coordinator@greenhill.local','Coordinator123!')
    r=client.get('/reports/release'); assert r.status_code==200; assert 'Release readiness' in r.text
