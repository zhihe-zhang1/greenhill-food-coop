import hashlib, hmac, os, secrets
from typing import Mapping

PBKDF2_ROUNDS = 180_000

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, PBKDF2_ROUNDS)
    return f'pbkdf2_sha256${PBKDF2_ROUNDS}${salt.hex()}${digest.hex()}'

def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, rounds, salt_hex, digest_hex = encoded.split('$', 3)
        if algo != 'pbkdf2_sha256': return False
        candidate = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt_hex), int(rounds))
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except Exception:
        return False

def ensure_csrf(session: Mapping) -> str:
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(24)
        session['csrf_token'] = token
    return token

def valid_csrf(session: Mapping, supplied: str | None) -> bool:
    expected = session.get('csrf_token', '')
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))
