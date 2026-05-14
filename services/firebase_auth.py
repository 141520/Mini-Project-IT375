"""Firebase Admin SDK initialization & ID token verification.

Setup:
1. Firebase Console → Project Settings → Service accounts → Generate new private key
2. Save downloaded JSON as `firebase-key.json` ที่ root ของ project
3. (อย่า commit ขึ้น git! เพิ่มใน .gitignore)
"""
import os
from typing import Optional

_initialized = False
_fb_auth = None


def _init():
    global _initialized, _fb_auth
    if _initialized:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials, auth as fb_auth

        key_path = os.environ.get("FIREBASE_KEY_PATH", "firebase-key.json")
        if not os.path.exists(key_path):
            print(f"[firebase] ⚠️ key file not found: {key_path} — Google login disabled")
            _initialized = True
            return

        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        _fb_auth = fb_auth
        print("[firebase] ✅ initialized")
    except Exception as e:
        print(f"[firebase] init failed: {e}")
    _initialized = True


def verify_id_token(id_token: str) -> Optional[dict]:
    """Verify Firebase ID token. Returns decoded claims or None."""
    _init()
    if _fb_auth is None:
        return None
    try:
        return _fb_auth.verify_id_token(id_token)
    except Exception as e:
        print(f"[firebase] verify failed: {e}")
        return None
