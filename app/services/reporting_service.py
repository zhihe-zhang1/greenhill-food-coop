from collections import defaultdict
from ..db import all_rows
from .pricing import line_total_cents

def round_totals(round_id):
    rows=all_rows('''SELECT p.id,p.name,p.sale_type,p.bay,rp.price_cents,ol.requested_milli,ol.packed_milli,o.status
      FROM round_products rp JOIN products p ON p.id=rp.product_id
      LEFT JOIN order_lines ol ON ol.round_product_id=rp.id
      LEFT JOIN orders o ON o.id=ol.order_id
      WHERE rp.round_id=? ORDER BY p.name''',(round_id,))
    out={}
    for r in rows:
        d=out.setdefault(r['id'],dict(name=r['name'],sale_type=r['sale_type'],bay=r['bay'],price_cents=r['price_cents'],requested_milli=0,packed_milli=0,order_count=0,total_cents=0))
        if r['requested_milli'] is not None and r['status']!='cancelled':
            d['requested_milli']+=r['requested_milli']; d['order_count']+=1
            if r['packed_milli'] is not None: d['packed_milli']+=r['packed_milli']
            d['total_cents']+=line_total_cents(r['price_cents'],r['requested_milli'],r['sale_type'])
    return list(out.values())

def packing_rows(round_id):
    return all_rows('''SELECT ol.id line_id,ol.requested_milli,ol.packed_milli,ol.packer_initials,ol.note,
      u.member_no,u.name member_name,u.crate_no,p.name product_name,p.sale_type,p.bay,rp.price_cents,o.id order_id
      FROM orders o JOIN users u ON u.id=o.user_id JOIN order_lines ol ON ol.order_id=o.id
      JOIN round_products rp ON rp.id=ol.round_product_id JOIN products p ON p.id=rp.product_id
      WHERE o.round_id=? AND o.status='submitted'
      ORDER BY COALESCE(u.crate_no,9999),p.bay,p.name''',(round_id,))
