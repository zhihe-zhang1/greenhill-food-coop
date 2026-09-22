import os,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
_tmp=tempfile.TemporaryDirectory(); os.environ['APP_DB_PATH']=str(Path(_tmp.name)/'test.db')
os.environ['APP_SECRET']='test-secret'
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db,seed_demo

@pytest.fixture(scope='session',autouse=True)
def db(): init_db(); seed_demo(); yield

@pytest.fixture
def client():
    with TestClient(app) as c: yield c
