from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings

from database import get_db
from models import User
from schemas.user import UserRegister, UserLogin, UserOut, Token
from auth import hash_password, verify_password, create_access_token, get_current_user
from services import firebase_auth as fb


class FirebaseLogin(BaseModel):
    id_token: str

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
        path="/",
    )


@router.post("/register", response_model=Token)
def register(data: UserRegister, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == data.username) | (User.email == data.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.username, user.role)
    _set_auth_cookie(response, token)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token = create_access_token(user.username, user.role)
    _set_auth_cookie(response, token)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/firebase-login", response_model=Token)
def firebase_login(payload: FirebaseLogin, response: Response, db: Session = Depends(get_db)):
    """Login ด้วย Firebase ID Token (Google Sign-in)
    - verify token กับ Firebase Admin SDK
    - ถ้าผู้ใช้ยังไม่มี → สร้าง user ใหม่ (role=user)
    - ออก JWT ของระบบเราเอง + set cookie
    """
    decoded = fb.verify_id_token(payload.id_token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid Firebase token (ตรวจสอบ firebase-key.json)")

    email = decoded.get("email")
    name = decoded.get("name") or (email.split("@")[0] if email else "user")
    if not email:
        raise HTTPException(status_code=400, detail="Token ไม่มี email")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        # สร้าง username ที่ไม่ซ้ำ
        base = name.replace(" ", "_").lower()[:40] or "user"
        username = base
        i = 1
        while db.query(User).filter(User.username == username).first():
            i += 1
            username = f"{base}{i}"
        user = User(
            username=username,
            email=email,
            password_hash="firebase",  # ไม่ใช้รหัสผ่าน
            role="user",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token = create_access_token(user.username, user.role)
    _set_auth_cookie(response, token)
    return Token(access_token=token, user=UserOut.model_validate(user))
