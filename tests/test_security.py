import re

from app.security import ensure_csrf, hash_password, valid_csrf, verify_password

PBKDF2_PREFIX = 'pbkdf2_sha256$'


def _csrf(client, path='/login'):
    """Render a page and pull the CSRF token the templates embed."""
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


def test_password_hash_round_trip():
    encoded=hash_password('hello-123')
    assert encoded!='hello-123'
    assert verify_password('hello-123',encoded)
    assert not verify_password('wrong',encoded)


def test_hash_uses_pbkdf2_and_a_random_salt():
    first, second = hash_password('same-password'), hash_password('same-password')
    assert first.startswith(PBKDF2_PREFIX) and second.startswith(PBKDF2_PREFIX)
    # A random per-hash salt means identical passwords never share a digest.
    assert first != second
    assert verify_password('same-password', first)
    assert verify_password('same-password', second)


def test_verify_password_rejects_malformed_encodings():
    not_a_hash = [
        '',
        'plaintext',
        'pbkdf2_sha256$only-three-parts',
        'md5$1$aa$bb',
        'pbkdf2_sha256$180000$nothex$nothex',
    ]
    for encoded in not_a_hash:
        assert verify_password('whatever', encoded) is False


def test_csrf_token_is_stable_within_a_session_and_strictly_validated():
    session = {}
    token = ensure_csrf(session)
    assert token and ensure_csrf(session) == token
    assert valid_csrf(session, token) is True
    assert valid_csrf(session, None) is False
    assert valid_csrf(session, '') is False
    assert valid_csrf(session, 'tampered-token') is False
    assert valid_csrf({}, token) is False


def test_login_rejects_wrong_password(client):
    response = _login(client, 'member@greenhill.local', 'not-the-password')
    assert 'Invalid email or password' in response.text
    assert client.get('/member').status_code == 401


def test_login_rejects_unknown_account(client):
    response = _login(client, 'nobody@greenhill.local', 'Member123!')
    assert 'Invalid email or password' in response.text


def test_login_rejects_a_stale_csrf_token(client):
    client.get('/login')
    response = client.post(
        '/login',
        data={'email': 'member@greenhill.local', 'password': 'Member123!', 'csrf_token': 'stale'},
    )
    assert response.status_code == 403


def test_logout_clears_the_session(client):
    _login(client, 'member@greenhill.local', 'Member123!')
    assert client.get('/member').status_code == 200
    client.post('/logout', data={'csrf_token': _csrf(client, '/member')}, follow_redirects=True)
    assert client.get('/member').status_code == 401


def test_anonymous_visitors_are_blocked_from_the_member_area(client):
    assert client.get('/member').status_code == 401
    assert client.get('/member/products').status_code == 401


def test_member_role_cannot_open_the_coordinator_area(client):
    _login(client, 'member@greenhill.local', 'Member123!')
    assert client.get('/coordinator').status_code == 403


def test_packer_role_cannot_open_the_member_area(client):
    _login(client, 'packer@greenhill.local', 'Packer123!')
    assert client.get('/member').status_code == 403
