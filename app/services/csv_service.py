import csv
from io import StringIO
from ..db import all_rows
from .pricing import line_total_cents, milli_to_quantity, money


def round_export_rows(round_id: int):
    return all_rows('''
        SELECT r.number round_number,u.member_no,u.name member_name,u.crate_no,
               p.name product_name,p.sale_type,p.bay,rp.price_cents,
               ol.requested_milli,ol.packed_milli,ol.packer_initials,ol.note
        FROM orders o
        JOIN rounds r ON r.id=o.round_id
        JOIN users u ON u.id=o.user_id
        JOIN order_lines ol ON ol.order_id=o.id
        JOIN round_products rp ON rp.id=ol.round_product_id
        JOIN products p ON p.id=rp.product_id
        WHERE o.round_id=? AND o.status='submitted'
        ORDER BY COALESCE(u.crate_no,9999),u.member_no,p.name
    ''',(round_id,))


def round_csv_text(round_id: int) -> str:
    out=StringIO(newline='')
    w=csv.writer(out)
    w.writerow(['Round','Member No','Member','Crate','Product','Sale Type','Bay','Unit Price','Requested','Packed','Requested Total','Packed Total','Packer','Note'])
    for r in round_export_rows(round_id):
        packed=r['packed_milli'] if r['packed_milli'] is not None else ''
        requested_total=line_total_cents(r['price_cents'],r['requested_milli'],r['sale_type'])
        packed_total=line_total_cents(r['price_cents'],r['packed_milli'],r['sale_type']) if r['packed_milli'] is not None else 0
        w.writerow([
            r['round_number'],r['member_no'],r['member_name'],r['crate_no'] or '',r['product_name'],r['sale_type'],r['bay'],
            money(r['price_cents']),milli_to_quantity(r['requested_milli'],r['sale_type']),
            milli_to_quantity(packed,r['sale_type']) if packed!='' else '',money(requested_total),money(packed_total) if packed!='' else '',
            r['packer_initials'],r['note']
        ])
    return out.getvalue()
