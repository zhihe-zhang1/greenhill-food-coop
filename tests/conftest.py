import itertools
import os,tempfile,sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
_tmp=tempfile.TemporaryDirectory(); os.environ['APP_DB_PATH']=str(Path(_tmp.name)/'test.db')
os.environ['APP_SECRET']='test-secret'
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db,seed_demo,one,execute
from app.services.order_service import save_member_order

@pytest.fixture(scope='session',autouse=True)
def db(): init_db(); seed_demo(); yield

@pytest.fixture
def client():
    with TestClient(app) as c: yield c


def csrf_token_from(html: str) -> str:
    """Extract the per-session CSRF token from any rendered form."""
    return html.split('name="csrf_token" value="',1)[1].split('"',1)[0]


@pytest.fixture
def csrf_of():
    return csrf_token_from


@pytest.fixture
def login(client):
    def _login(email: str, password: str, follow: bool = True):
        r=client.get('/login'); token=csrf_token_from(r.text)
        return client.post('/login',data={'email':email,'password':password,'csrf_token':token},follow_redirects=follow)
    return _login


@pytest.fixture
def logout(client):
    def _logout(follow: bool = True):
        page=client.get('/',follow_redirects=True); token=csrf_token_from(page.text)
        return client.post('/logout',data={'csrf_token':token},follow_redirects=follow)
    return _logout


# Round numbers are unique in the schema, so the shared helper allocates from a high
# range that cannot collide with the seeded demo round (35) or with the numbers used
# by other test modules.
_round_numbers=itertools.count(5000)

@pytest.fixture
def new_round():
    """Create an isolated open round with its product price snapshot, so tests never
    share order rows and never depend on the seeded demo round."""
    def _new_round(number: int | None = None, status: str = 'open', closes_in_days: int = 6):
        number = number if number is not None else next(_round_numbers)
        now=datetime.now().replace(microsecond=0)
        rid=execute('INSERT INTO rounds(number,opens_at,closes_at,pickup_at,status) VALUES(?,?,?,?,?)',
                    (number,(now-timedelta(days=1)).isoformat(' '),
                     (now+timedelta(days=closes_in_days)).isoformat(' '),
                     (now+timedelta(days=closes_in_days+3)).isoformat(' '),status))
        execute('INSERT INTO round_products(round_id,product_id,price_cents,available) SELECT ?,id,price_cents,active FROM products',(rid,))
        return rid
    return _new_round


@pytest.fixture
def place_order():
    """Submit an order and return (order_id, order_line_row)."""
    def _place(round_id: int, member_email: str, product_name: str, quantity: str = '1'):
        user=one('SELECT * FROM users WHERE email=?',(member_email,))
        rp=one('''SELECT rp.id FROM round_products rp JOIN products p ON p.id=rp.product_id
                  WHERE rp.round_id=? AND p.name=?''',(round_id,product_name))
        oid=save_member_order(round_id,user['id'],{rp['id']:quantity})
        return oid,one('SELECT * FROM order_lines WHERE order_id=?',(oid,))
    return _place
