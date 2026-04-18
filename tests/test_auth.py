"""Test JWT auth."""
from auth import hash_password, verify_password, create_access_token, decode_token


def test_password_hash_verify():
    pw = "mysecret123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)
    assert not verify_password("wrong", hashed)


def test_token_roundtrip():
    token = create_access_token("alice", "user")
    payload = decode_token(token)
    assert payload["sub"] == "alice"
    assert payload["role"] == "user"
    assert "exp" in payload
