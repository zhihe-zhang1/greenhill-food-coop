from decimal import Decimal, ROUND_HALF_UP

def quantity_to_milli(value: str, sale_type: str) -> int:
    q = Decimal(str(value or '0').strip())
    if q <= 0: return 0
    if sale_type == 'unit' and q != q.to_integral_value():
        raise ValueError('Unit products require a whole-number quantity.')
    milli = (q * 1000).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return int(milli)

def milli_to_quantity(milli: int | None, sale_type: str) -> str:
    if milli is None: return ''
    q = Decimal(milli) / Decimal(1000)
    if sale_type == 'unit': return str(int(q))
    return f'{q.normalize():f}'

def line_total_cents(price_cents: int, qty_milli: int, sale_type: str) -> int:
    if sale_type == 'unit':
        if qty_milli % 1000: raise ValueError('Unit quantity must be a whole number.')
        return price_cents * (qty_milli // 1000)
    amount = (Decimal(price_cents) * Decimal(qty_milli) / Decimal(1000)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return int(amount)

def money(cents: int | None) -> str:
    return f'${(Decimal(cents or 0) / 100):,.2f}'
