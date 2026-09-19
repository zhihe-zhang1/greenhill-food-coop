import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from .config import settings
from .security import hash_password

SCHEMA = r'''
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_no TEXT UNIQUE,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT DEFAULT '',
    address TEXT DEFAULT '',
    crate_no INTEGER,
    role TEXT NOT NULL DEFAULT 'member',
    active INTEGER NOT NULL DEFAULT 1,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    sale_type TEXT NOT NULL CHECK(sale_type IN ('unit','kg')),
    price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    bay TEXT DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER NOT NULL UNIQUE,
    opens_at TEXT NOT NULL,
    closes_at TEXT NOT NULL,
    pickup_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','closed','packed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS round_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER NOT NULL REFERENCES rounds(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    price_cents INTEGER NOT NULL,
    available INTEGER NOT NULL DEFAULT 1,
    UNIQUE(round_id, product_id)
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id INTEGER NOT NULL REFERENCES rounds(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'submitted' CHECK(status IN ('submitted','cancelled')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(round_id, user_id)
);
CREATE TABLE IF NOT EXISTS order_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    round_product_id INTEGER NOT NULL REFERENCES round_products(id),
    requested_milli INTEGER NOT NULL CHECK(requested_milli > 0),
    packed_milli INTEGER,
    packer_initials TEXT DEFAULT '',
    note TEXT DEFAULT '',
    UNIQUE(order_id, round_product_id)
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    detail TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
'''

@contextmanager
def connect():
    con = sqlite3.connect(settings.db_path)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with connect() as con:
        con.executescript(SCHEMA)

def one(sql, params=()):
    with connect() as con: return con.execute(sql, params).fetchone()

def all_rows(sql, params=()):
    with connect() as con: return con.execute(sql, params).fetchall()

def execute(sql, params=()):
    with connect() as con:
        cur=con.execute(sql, params)
        return cur.lastrowid

def seed_demo():
    if one('SELECT id FROM users LIMIT 1'): return
    now = datetime.now().replace(microsecond=0)
    open_at = now - timedelta(days=1)
    close_at = now + timedelta(days=2)
    pickup = now + timedelta(days=5)
    with connect() as con:
        users=[
            ('COORD-1','Ngaire Fletcher','coordinator@greenhill.local','0400 000 001','Moorooka QLD',1,'coordinator','Coordinator123!'),
            ('PACK-1','Bao Nguyen','packer@greenhill.local','0400 000 002','Moorooka QLD',2,'packer','Packer123!'),
            ('M-094','Ky Tran','member@greenhill.local','0438 601 772','Moorooka QLD',14,'member','Member123!'),
            ('M-063','Jan Buckley','jan@example.local','0400 000 063','Moorooka QLD',11,'member','Member123!'),
            ('M-118','Ada Okonkwo','ada@example.local','0400 000 118','Moorooka QLD',19,'member','Member123!'),
        ]
        for member_no,name,email,phone,address,crate,role,pwd in users:
            con.execute('INSERT INTO users(member_no,name,email,phone,address,crate_no,role,password_hash) VALUES(?,?,?,?,?,?,?,?)',
                        (member_no,name,email,phone,address,crate,role,hash_password(pwd)))
        products=[
            ('Rolled oats, organic','Bulk organic rolled oats','kg',340,'B1'),
            ('Brown rice, medium','Medium grain brown rice','kg',410,'B3'),
            ('Red lentils, split','Bulk red lentils','kg',485,'B4'),
            ('Coffee beans, whole','Whole coffee beans','kg',3200,'C2'),
            ('Tahini, 375 g jar','375 gram jar','unit',980,'A2'),
            ('Eggs, free range, dozen','One dozen free range eggs','unit',750,'COOL'),
            ('Pumpkin (Two Creeks)','Seasonal pumpkin','kg',260,'VEG'),
            ('Olive oil, 1 L tin','One litre tin','unit',1960,'A1'),
            ('Peanut butter, 500 g jar','500 gram jar','unit',840,'A2'),
            ('Raw almonds','Raw almonds','kg',1890,'C1'),
            ('Carrots (Two Creeks)','Fresh carrots','kg',320,'VEG'),
            ('Olive oil soap bar','Soap bar','unit',420,'A4')
        ]
        for row in products:
            con.execute('INSERT INTO products(name,description,sale_type,price_cents,bay) VALUES(?,?,?,?,?)',row)
        rid=con.execute('INSERT INTO rounds(number,opens_at,closes_at,pickup_at,status) VALUES(?,?,?,?,?)',
                        (35,open_at.isoformat(' '),close_at.isoformat(' '),pickup.isoformat(' '),'open')).lastrowid
        con.execute('INSERT INTO round_products(round_id,product_id,price_cents,available) SELECT ?,id,price_cents,active FROM products',(rid,))
