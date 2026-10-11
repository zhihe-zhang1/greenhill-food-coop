from ..db import one
from .reporting_service import round_totals


def round_metrics(round_id: int):
    row=one('''SELECT
        COUNT(DISTINCT CASE WHEN o.status='submitted' THEN o.id END) order_count,
        COUNT(DISTINCT CASE WHEN o.status='submitted' THEN o.user_id END) member_count,
        COUNT(CASE WHEN o.status='submitted' THEN ol.id END) line_count,
        COUNT(CASE WHEN o.status='submitted' AND ol.packed_milli IS NOT NULL THEN ol.id END) packed_line_count
        FROM orders o LEFT JOIN order_lines ol ON ol.order_id=o.id WHERE o.round_id=?''',(round_id,))
    totals=round_totals(round_id)
    estimated=sum(x['total_cents'] for x in totals)
    requested=sum(x['requested_milli'] for x in totals)
    packed=sum(x['packed_milli'] for x in totals)
    lines=row['line_count'] or 0
    packed_lines=row['packed_line_count'] or 0
    return {
        'order_count':row['order_count'] or 0,
        'member_count':row['member_count'] or 0,
        'line_count':lines,
        'packed_line_count':packed_lines,
        'packing_percent':round((packed_lines/lines)*100) if lines else 0,
        'estimated_cents':estimated,
        'requested_milli':requested,
        'packed_milli':packed,
    }
