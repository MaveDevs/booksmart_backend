from datetime import timedelta

from jose import jwt

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_and_verify_flow():
    plain_password = "mike123"
    hashed = get_password_hash(plain_password)

    assert hashed != plain_password
    assert verify_password(plain_password, hashed) is True


def test_access_token_contains_subject_claim():
    token = create_access_token(subject=123, expires_delta=timedelta(minutes=5))
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["sub"] == "123"
    assert "exp" in payload
