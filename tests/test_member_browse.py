"""Member-side browsing: current round products and the personal dashboard.

Story: MSD426GXUST34-8
"""
import re


def _csrf(client, path='/login'):
    page = client.get(path, follow_redirects=True)
    match = re.search(r'name="csrf_token" value="([^"]+)"', page.text)
    assert match, f'no csrf_token found while loading {path}'
    return match.group(1)


def _login(client, email, password):
    return client.post(
        '/login',
        data={'email': email, 'password': password, 'csrf_token': _csrf(client)},
        follow_redirects=True,
    )


def _member(client):
    _login(client, 'member@greenhill.local', 'Member123!')


def test_member_pages_require_login(client):
    assert client.get('/member').status_code == 401
    assert client.get('/member/products').status_code == 401


def test_dashboard_shows_greeting_current_round_and_history(client):
    _member(client)
    response = client.get('/member')
    assert response.status_code == 200
    assert 'MEMBER HOME' in response.text
    assert 'Hello' in response.text
    assert 'Current round' in response.text
    assert 'Recent orders' in response.text


def test_products_page_lists_the_current_round_catalogue(client):
    _member(client)
    response = client.get('/member/products')
    assert response.status_code == 200
    assert 'Available products' in response.text
    # the page must say the prices come from this round's snapshot
    assert 'price snapshots for this round' in response.text
    # seeded catalogue for the open round
    assert 'Rolled oats' in response.text
    assert 'Eggs, free range' in response.text


def test_products_for_round_only_returns_available_active_items(client):
    from app.services.order_service import current_open_round, products_for_round

    round_row = current_open_round()
    items = products_for_round(round_row['id'])
    assert items, 'the seeded open round should expose products'
    assert all(item['available'] == 1 and item['active'] == 1 for item in items)


def test_unavailable_product_disappears_from_the_member_view(client):
    """A product the coordinator marks unavailable must drop off the member pages."""
    from app.db import execute
    from app.services.order_service import current_open_round, products_for_round

    _member(client)
    round_row = current_open_round()
    oats = next(p for p in products_for_round(round_row['id']) if p['name'].startswith('Rolled oats'))
    execute('UPDATE round_products SET available=0 WHERE id=?', (oats['round_product_id'],))
    try:
        assert 'Rolled oats' not in client.get('/member/products').text
        still_listed = products_for_round(round_row['id'])
        assert all(p['round_product_id'] != oats['round_product_id'] for p in still_listed)
    finally:
        execute('UPDATE round_products SET available=1 WHERE id=?', (oats['round_product_id'],))
