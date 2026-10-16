"""Round report, CSV export and metrics tests - member C scope (GHC-A3-12).

The report is the coordinator's release evidence: totals, packing completion and
a downloadable CSV of the round. The tests check the access rule, the exported
content and that cancelled orders never reach the report or the CSV.
"""
from app.db import one, execute, all_rows
from app.services.order_service import cancel_order
from app.services.metrics_service import round_metrics
from app.services.csv_service import round_csv_text

COORDINATOR=('coordinator@greenhill.local','Coordinator123!')
MEMBER=('member@greenhill.local','Member123!')
MEMBER_2=('jan@example.local','Member123!')

KG_PRODUCT='Rolled oats, organic'
UNIT_PRODUCT='Tahini, 375 g jar'


def login(client,email,password):
    r=client.get('/login'); token=r.text.split('name="csrf_token" value="',1)[1].split('"',1)[0]
    return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=True)


def test_coordinator_round_report_and_csv(client):
    login(client,'coordinator@greenhill.local','Coordinator123!')
    rid=one('SELECT id FROM rounds ORDER BY number DESC LIMIT 1')['id']
    r=client.get(f'/reports/round/{rid}'); assert r.status_code==200; assert 'Round #' in r.text
    csv=client.get(f'/reports/round/{rid}/csv'); assert csv.status_code==200; assert 'Member No' in csv.text


def test_release_readiness(client):
    login(client,'coordinator@greenhill.local','Coordinator123!')
    r=client.get('/reports/release'); assert r.status_code==200; assert 'Release readiness' in r.text


def test_report_and_csv_require_the_coordinator_role(client, login):
    rid=one('SELECT id FROM rounds ORDER BY number DESC LIMIT 1')['id']
    assert client.get(f'/reports/round/{rid}').status_code==401
    assert client.get(f'/reports/round/{rid}/csv').status_code==401
    login(*MEMBER)
    assert client.get(f'/reports/round/{rid}').status_code==403
    assert client.get(f'/reports/round/{rid}/csv').status_code==403
    assert client.get('/reports/release').status_code==403


def test_report_for_an_unknown_round_redirects_to_the_round_list(client, login):
    login(*COORDINATOR)
    r=client.get('/reports/round/999999',follow_redirects=False)
    assert r.status_code==303 and r.headers['location']=='/coordinator/rounds'


def test_csv_for_an_unknown_round_returns_not_found(client, login):
    login(*COORDINATOR)
    assert client.get('/reports/round/999999/csv').status_code==404


def test_report_shows_the_round_totals_and_completion(client, login, new_round, place_order):
    rid=new_round()
    place_order(rid,MEMBER[0],KG_PRODUCT,'2')
    place_order(rid,MEMBER_2[0],UNIT_PRODUCT,'1')
    login(*COORDINATOR)
    page=client.get(f'/reports/round/{rid}')
    assert page.status_code==200
    assert KG_PRODUCT in page.text and UNIT_PRODUCT in page.text


def test_csv_export_is_downloadable_and_prefixed_for_excel(client, login, new_round, place_order):
    rid=new_round()
    place_order(rid,MEMBER[0],KG_PRODUCT,'2.5')
    login(*COORDINATOR)
    r=client.get(f'/reports/round/{rid}/csv')
    assert r.status_code==200
    assert 'attachment; filename=' in r.headers['content-disposition']
    assert r.text.startswith('\ufeff')
    assert 'M-094' in r.text and '2.5' in r.text


def test_csv_export_excludes_cancelled_orders(client, login, new_round, place_order):
    rid=new_round()
    place_order(rid,MEMBER[0],KG_PRODUCT,'2')
    cancelled,_=place_order(rid,MEMBER_2[0],UNIT_PRODUCT,'1')
    cancel_order(cancelled,one('SELECT id FROM users WHERE email=?',(MEMBER_2[0],))['id'])
    text=round_csv_text(rid)
    assert 'M-094' in text and KG_PRODUCT in text
    assert 'M-063' not in text and UNIT_PRODUCT not in text


def test_round_metrics_report_packing_completion(client, new_round, place_order):
    rid=new_round()
    _,line_a=place_order(rid,MEMBER[0],KG_PRODUCT,'2')
    place_order(rid,MEMBER_2[0],UNIT_PRODUCT,'1')
    execute('UPDATE order_lines SET packed_milli=2000 WHERE id=?',(line_a['id'],))
    m=round_metrics(rid)
    assert m['order_count']==2 and m['member_count']==2 and m['line_count']==2
    assert m['packed_line_count']==1 and m['packing_percent']==50
    assert m['requested_milli']==3000 and m['packed_milli']==2000


def test_round_metrics_ignore_cancelled_orders(client, new_round, place_order):
    rid=new_round()
    place_order(rid,MEMBER[0],KG_PRODUCT,'2')
    cancelled,_=place_order(rid,MEMBER_2[0],KG_PRODUCT,'3')
    cancel_order(cancelled,one('SELECT id FROM users WHERE email=?',(MEMBER_2[0],))['id'])
    m=round_metrics(rid)
    assert m['order_count']==1 and m['line_count']==1
    assert m['requested_milli']==2000
