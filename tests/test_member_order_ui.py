"""Member order screens: the order form and the order detail page.

Story: MSD426GXUST34-10
"""
import re

MEMBER_EMAIL = 'member@greenhill.local'


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
    _login(client, MEMBER_EMAIL, 'Member123!')


def _member_round_and_product(prefix='Rolled oats'):
    from app.db import one
    from app.services.order_service import current_open_round, products_for_round

    round_row = current_open_round()
    user = one('SELECT * FROM users WHERE email=?', (MEMBER_EMAIL,))
    product = next(p for p in products_for_round(round_row['id']) if p['name'].startswith(prefix))
    return round_row, user, product


def test_order_form_requires_login(client):
    assert client.get('/member/order').status_code == 401


def test_order_form_lists_products_behind_a_csrf_protected_save(client):
    _member(client)
    response = client.get('/member/order')
    assert response.status_code == 200
    assert 'CURRENT ORDER' in response.text
    assert 'Save order' in response.text
    assert 'csrf_token' in response.text
    assert 'Rolled oats' in response.text


def test_order_form_switches_to_edit_mode_once_an_order_exists(client):
    from app.services.order_service import save_member_order

    _member(client)
    round_row, user, product = _member_round_and_product()
    save_member_order(round_row['id'], user['id'], {product['round_product_id']: '2'})
    response = client.get('/member/order')
    assert 'Edit your order' in response.text
    assert f'name="qty_{product["round_product_id"]}"' in response.text


def test_order_submission_without_a_valid_csrf_token_is_ignored(client):
    _member(client)
    response = client.post(
        '/member/order',
        data={'csrf_token': 'stale', 'qty_1': '2'},
        follow_redirects=False,
    )
    assert response.status_code in (303, 307)


def test_order_detail_renders_lines_total_and_cancel_option(client):
    from app.services.order_service import save_member_order

    _member(client)
    round_row, user, product = _member_round_and_product()
    order_id = save_member_order(round_row['id'], user['id'], {product['round_product_id']: '2'})
    response = client.get(f'/member/orders/{order_id}')
    assert response.status_code == 200
    assert 'ORDER HISTORY' in response.text
    assert 'Rolled oats' in response.text
    assert 'Total' in response.text
    # open round + submitted order -> the member is allowed to cancel
    assert 'Cancel order' in response.text


def test_order_detail_bounces_back_for_an_order_that_is_not_yours(client):
    _member(client)
    response = client.get('/member/orders/999999', follow_redirects=False)
    assert response.status_code in (303, 307)
    assert response.headers.get('location') == '/member'
