import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from config import settings
from database import get_db
from models import BoardGame, User, Message, Conversation
from auth import require_admin
from services import pdf_parser, vector_store

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/games")
def create_game(
    name: str = Form(...),
    description: str = Form(""),
    language: str = Form("th"),
    category: str = Form(""),
    image: UploadFile = File(None),
    pdf: UploadFile = File(None),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    game = BoardGame(name=name, description=description, language=language, category=category or None)
    db.add(game)
    db.commit()
    db.refresh(game)

    if image and image.filename:
        img_path = os.path.join(settings.UPLOAD_DIR, f"game_{game.id}_{image.filename}")
        with open(img_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        game.image = f"/static/uploads/game_{game.id}_{image.filename}"

    if pdf and pdf.filename:
        pdf_path = os.path.join(settings.UPLOAD_DIR, f"game_{game.id}_{pdf.filename}")
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(pdf.file, f)
        game.pdf_path = pdf_path

    db.commit()
    return {"id": game.id, "message": "Game created. Use /games/{id}/index to index PDF."}


@router.post("/games/{game_id}/index")
def index_game(game_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    game = db.get(BoardGame, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not game.pdf_path or not os.path.exists(game.pdf_path):
        raise HTTPException(status_code=400, detail="PDF not uploaded")

    try:
        chunks = pdf_parser.chunk_pdf(game.pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF parse error: {e}")

    if not chunks:
        # Try to diagnose why
        try:
            from services.pdf_parser import extract_pages
            raw_pages = extract_pages(game.pdf_path)
            if not raw_pages:
                raise HTTPException(status_code=422, detail="PDF ไม่มีข้อความ (อาจเป็น PDF สแกน/รูปภาพ) — ต้องใช้ PDF ที่มีข้อความจริง")
            raise HTTPException(status_code=422, detail=f"PDF มี {len(raw_pages)} หน้าแต่ chunk ไม่ได้ — ลองอัปโหลดใหม่")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"PDF อ่านได้แต่ chunk ไม่สำเร็จ: {e}")

    count = vector_store.index_chunks(game.id, chunks)
    pages = len({c["page"] for c in chunks})

    game.is_indexed = True
    game.total_pages = pages
    db.commit()

    return {"indexed_chunks": count, "pages": pages}


@router.delete("/games/{game_id}")
def delete_game(game_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    game = db.get(BoardGame, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    vector_store.delete_game(game.id)
    if game.pdf_path and os.path.exists(game.pdf_path):
        try:
            os.remove(game.pdf_path)
        except OSError:
            pass
    db.delete(game)
    db.commit()
    return {"status": "deleted"}


@router.get("/stats")
def stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {
        "total_users": db.query(User).count(),
        "total_games": db.query(BoardGame).count(),
        "indexed_games": db.query(BoardGame).filter(BoardGame.is_indexed == True).count(),
        "total_conversations": db.query(Conversation).count(),
        "total_messages": db.query(Message).count(),
        "top_questions": [
            {"content": r.content, "count": r.c}
            for r in db.query(Message.content, func.count(Message.id).label("c"))
            .filter(Message.role == "user")
            .group_by(Message.content)
            .order_by(func.count(Message.id).desc())
            .limit(10)
            .all()
        ],
    }


@router.get("/analytics")
def analytics(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    days = [(today - timedelta(days=i)) for i in range(13, -1, -1)]
    day_labels = [d.strftime("%m-%d") for d in days]

    # messages per day (user questions only)
    counts_by_day = []
    for d in days:
        start = datetime.combine(d, datetime.min.time())
        end = start + timedelta(days=1)
        c = db.query(Message).filter(
            Message.role == "user",
            Message.created_at >= start,
            Message.created_at < end,
        ).count()
        counts_by_day.append(c)

    # top games by question count
    game_counts = (
        db.query(BoardGame.name, func.count(Message.id).label("c"))
        .join(Conversation, Conversation.game_id == BoardGame.id)
        .join(Message, Message.conversation_id == Conversation.id)
        .filter(Message.role == "user")
        .group_by(BoardGame.id)
        .order_by(func.count(Message.id).desc())
        .limit(8)
        .all()
    )

    # ratings per game
    rating_data = (
        db.query(
            BoardGame.name,
            func.sum(func.iif(Message.rating == 1, 1, 0)).label("up"),
            func.sum(func.iif(Message.rating == -1, 1, 0)).label("down"),
        )
        .join(Conversation, Conversation.game_id == BoardGame.id)
        .join(Message, Message.conversation_id == Conversation.id)
        .filter(Message.role == "assistant", Message.rating != 0)
        .group_by(BoardGame.id)
        .all()
    )

    return {
        "daily": {"labels": day_labels, "counts": counts_by_day},
        "top_games": {"labels": [g[0] for g in game_counts], "counts": [g[1] for g in game_counts]},
        "ratings": {
            "labels": [r[0] for r in rating_data],
            "up": [int(r[1] or 0) for r in rating_data],
            "down": [int(r[2] or 0) for r in rating_data],
        },
    }


@router.get("/users")
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/users/{user_id}/toggle")
def toggle_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.is_active = not u.is_active
    db.commit()
    return {"id": u.id, "is_active": u.is_active}
