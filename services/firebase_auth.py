"""Firebase ID token verification — ไม่ต้องใช้ Service Account Key
ใช้ Google Public Keys verify JWT โดยตรง (pyjwt + httpx)
"""
import time
from datetime import timedelta
from typing import Optional
import httpx
import jwt
from cryptography import x509

# Google Public Keys สำหรับ Firebase ID tokens
_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_FIREBASE_PROJECT_ID = "ig342-f1cc4"

_certs_cache: dict = {}
_certs_expiry: float = 0


def _get_google_certs() -> dict:
    """ดึง Google Public Keys (cache ตาม Cache-Control header)"""
    global _certs_cache, _certs_expiry
    if _certs_cache and time.time() < _certs_expiry:
        return _certs_cache
    try:
        r = httpx.get(_CERTS_URL, timeout=5)
        r.raise_for_status()
        _certs_cache = r.json()
        # อ่าน max-age จาก Cache-Control
        cc = r.headers.get("cache-control", "")
        max_age = 3600
        for part in cc.split(","):
            part = part.strip()
            if part.startswith("max-age="):
                try:
                    max_age = int(part.split("=")[1])
                except Exception:
                    pass
        _certs_expiry = time.time() + max_age
        print(f"[firebase] certs fetched, cache {max_age}s")
    except Exception as e:
        if _certs_cache:
            print(f"[firebase] fetch certs error (using stale cache): {e}")
        else:
            print(f"[firebase] fetch certs error (no cache): {e}")
    return _certs_cache


def verify_id_token(id_token: str) -> Optional[dict]:
    """Verify Firebase ID token ด้วย Google Public Keys (X.509 PEM certs)
    Returns decoded claims dict หรือ None ถ้าไม่ valid
    """
    try:
        certs = _get_google_certs()
        if not certs:
            print("[firebase] no certs available")
            return None

        # ถอด header เพื่อเอา kid
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            print("[firebase] token missing kid header")
            return None
        if kid not in certs:
            print(f"[firebase] kid '{kid}' not found in certs, available: {list(certs.keys())}")
            return None

        # แปลง X.509 PEM cert → RSA Public Key (pass key object directly, no PEM round-trip)
        cert = x509.load_pem_x509_certificate(certs[kid].encode("utf-8"))
        public_key = cert.public_key()

        expected_iss = f"https://securetoken.google.com/{_FIREBASE_PROJECT_ID}"
        decoded = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=_FIREBASE_PROJECT_ID,
            issuer=expected_iss,
            leeway=timedelta(seconds=10),
            options={"verify_exp": True},
        )

        if not decoded.get("email_verified"):
            print("[firebase] email not verified")
            return None

        print(f"[firebase] token OK: {decoded.get('email')}")
        return decoded

    except jwt.ExpiredSignatureError:
        print("[firebase] token expired")
        return None
    except Exception as e:
        print(f"[firebase] verify error: {type(e).__name__}: {e}")
        return None
