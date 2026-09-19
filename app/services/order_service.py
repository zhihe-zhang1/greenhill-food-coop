from datetime import datetime
from ..db import connect, one, all_rows
from .pricing import quantity_to_milli, line_total_cents

class OrderError(ValueError): pass

def current_open_round():
    return one("SELECT * FROM rounds WHERE status='open' ORDER BY number DESC LIMIT 1")

def round_is_editable(round_row):
    if not round_row or round_row['status'] != 'open': return False
    try: return datetime.fromisoformat(round_row['closes_at']) >= datetime.now()
    except Exception: return True

def products_for_round(round_id, include_unavailable=False):
    where='' if include_unavailable else 'AND rp.available=1 AND p.active=1'
    return all_rows(f'''SELECT rp.id round_product_id,rp.price_cents,rp.available,p.*
        FROM round_products rp JOIN products p ON p.id=rp.product_id
        WHERE rp.round_id=? {where} ORDER BY p.name''',(round_id,))

def member_order(round_id, user_id):
    return one('SELECT * FROM orders WHERE round_id=? AND user_id=?',(round_id,user_id))

def order_lines(order_id):
    return all_rows('''SELECT ol.*,rp.price_cents,p.name,p.sale_type,p.bay
        FROM order_lines ol JOIN round_products rp ON rp.id=ol.round_product_id
        JOIN products p ON p.id=rp.product_id WHERE ol.order_id=? ORDER BY p.name''',(order_id,))

def save_member_order(round_id, user_id, quantities: dict[int,str]):
    rnd=one('SELECT * FROM rounds WHERE id=?',(round_id,))
    if not round_is_editable(rnd): raise OrderError('This round is not open for ordering.')
    products={r['round_product_id']:r for r in products_for_round(round_id)}
    parsed=[]
    for rpid, raw in quantities.items():
        if rpid not in products: continue
        try: milli=quantity_to_milli(raw, products[rpid]['sale_type'])
        except Exception as e: raise OrderError(f"{products[rpid]['name']}: {e}")
        if milli>0: parsed.append((rpid,milli))
    if not parsed: raise OrderError('Add at least one product to submit an order.')
    with connect() as con:
        order=con.execute('SELECT * FROM orders WHERE round_id=? AND user_id=?',(round_id,user_id)).fetchone()
        if order:
            oid=order['id']; con.execute("UPDATE orders SET status='submitted',updated_at=CURRENT_TIMESTAMP WHERE id=?",(oid,)); con.execute('DELETE FROM order_lines WHERE order_id=?',(oid,))
        else:
            oid=con.execute('INSERT INTO orders(round_id,user_id,status) VALUES(?,?,\'submitted\')',(round_id,user_id)).lastrowid
        con.executemany('INSERT INTO order_lines(order_id,round_product_id,requested_milli) VALUES(?,?,?)',[(oid,rpid,m) for rpid,m in parsed])
    return oid

def cancel_order(order_id, user_id):
    order=one('''SELECT o.*,r.status round_status,r.closes_at FROM orders o JOIN rounds r ON r.id=o.round_id
                 WHERE o.id=? AND o.user_id=?''',(order_id,user_id))
    if not order: raise OrderError('Order not found.')
    if not round_is_editable(order): raise OrderError('Closed-round orders cannot be cancelled.')
    with connect() as con: con.execute("UPDATE orders SET status='cancelled',updated_at=CURRENT_TIMESTAMP WHERE id=?",(order_id,))

def order_total(order_id, packed=False):
    total=0
    for line in order_lines(order_id):
        qty=line['packed_milli'] if packed and line['packed_milli'] is not None else line['requested_milli']
        total+=line_total_cents(line['price_cents'],qty,line['sale_type'])
    return total
