"""Jinja web pages (user site + admin panel)."""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import BoardGame, User, Conversation
from auth import get_optional_user, get_current_user, require_admin

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _ctx(user, **extra):
    return {"current_user": user, **extra}


CATEGORIES = ["ครอบครัว", "ปาร์ตี้", "กลยุทธ์", "การ์ด", "เด็ก", "สองคน"]

@router.get("/", response_class=HTMLResponse)
def home(request: Request, q: str = "", cat: str = "", user=Depends(get_optional_user), db: Session = Depends(get_db)):
    query = db.query(BoardGame)
    q_clean = (q or "").strip()
    cat_clean = (cat or "").strip()
    if q_clean:
        like = f"%{q_clean}%"
        query = query.filter(
            (BoardGame.name.ilike(like)) | (BoardGame.description.ilike(like))
        )
    if cat_clean:
        query = query.filter(BoardGame.category == cat_clean)
    games = query.order_by(BoardGame.created_at.desc()).limit(48).all()
    return templates.TemplateResponse(request, "index.html",
        _ctx(user, games=games, q=q_clean, cat=cat_clean, categories=CATEGORIES))


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user=Depends(get_optional_user)):
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse(request, "login.html", _ctx(user))


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, user=Depends(get_optional_user)):
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse(request, "register.html", _ctx(user))


@router.get("/logout")
def logout():
    resp = RedirectResponse("/")
    resp.delete_cookie("access_token")
    return resp


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_optional_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse("/login")
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .limit(20)
        .all()
    )
    return templates.TemplateResponse(request, "dashboard.html", _ctx(user, conversations=convs))


@router.get("/games/{game_id}/chat", response_class=HTMLResponse)
def chat_page(game_id: int, request: Request, user=Depends(get_optional_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse("/login")
    game = db.get(BoardGame, game_id)
    if not game:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse(request, "chat.html", _ctx(user, game=game))


# ---------- Admin pages ----------

@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, user=Depends(get_optional_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse("/login")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    games = db.query(BoardGame).order_by(BoardGame.created_at.desc()).all()
    users = db.query(User).order_by(User.created_at.desc()).all()
    stats_data = {
        "users": len(users),
        "games": len(games),
        "indexed": sum(1 for g in games if g.is_indexed),
    }
    return templates.TemplateResponse(request, "admin/index.html", _ctx(user, games=games, users=users, stats=stats_data))
