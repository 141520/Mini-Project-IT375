import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from config import settings
from database import get_db
from models import BoardGame, User, Message, Conversation, GamePDF
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


@router.post("/games/{game_id}/pdfs")
def add_pdf(
    game_id: int,
    pdf: UploadFile = File(...),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    game = db.get(BoardGame, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    existing = db.query(GamePDF).filter(GamePDF.game_id == game_id).count()
    # count main PDF too
    main_count = 1 if (game.pdf_path and os.path.exists(game.pdf_path)) else 0
    if existing + main_count >= 5:
        raise HTTPException(status_code=400, detail="ใส่ PDF ได้สูงสุด 5 ไฟล์ต่อเกม")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = pdf.filename.replace(" ", "_")
    pdf_path = os.path.join(settings.UPLOAD_DIR, f"game_{game_id}_extra_{existing+1}_{safe_name}")
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    db.add(GamePDF(game_id=game_id, pdf_path=pdf_path, filename=pdf.filename))
    game.is_indexed = False  # ต้อง re-index
    db.commit()
    return {"message": f"เพิ่ม PDF '{pdf.filename}' สำเร็จ กรุณา Index ใหม่"}


@router.delete("/games/{game_id}/pdfs/{pdf_id}")
def delete_pdf(
    game_id: int,
    pdf_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    gp = db.query(GamePDF).filter(GamePDF.id == pdf_id, GamePDF.game_id == game_id).first()
    if not gp:
        raise HTTPException(status_code=404, detail="PDF not found")
    if os.path.exists(gp.pdf_path):
        os.remove(gp.pdf_path)
    db.delete(gp)
    db.commit()
    return {"status": "deleted"}


@router.post("/games/{game_id}/index")
def index_game(game_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    game = db.get(BoardGame, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # รวม PDF หลัก + PDF เพิ่มเติม
    pdf_paths = []
    if game.pdf_path and os.path.exists(game.pdf_path):
        pdf_paths.append(game.pdf_path)
    for gp in db.query(GamePDF).filter(GamePDF.game_id == game_id).all():
        if os.path.exists(gp.pdf_path):
            pdf_paths.append(gp.pdf_path)

    if not pdf_paths:
        raise HTTPException(status_code=400, detail="ไม่มีไฟล์ PDF — กรุณาอัปโหลดก่อน")

    all_chunks = []
    for path in pdf_paths:
        try:
            all_chunks.extend(pdf_parser.chunk_pdf(path))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF parse error ({os.path.basename(path)}): {e}")

    if not all_chunks:
        raise HTTPException(status_code=422, detail="PDF ไม่มีข้อความ — อาจเป็น PDF สแกน/รูปภาพ")

    count = vector_store.index_chunks(game.id, all_chunks)
    pages = len({c["page"] for c in all_chunks})

    game.is_indexed = True
    game.total_pages = pages
    db.commit()

    return {"indexed_chunks": count, "pages": pages, "pdf_count": len(pdf_paths)}


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


@router.post("/users")
def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from auth import hash_password
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(status_code=400, detail="Username นี้มีอยู่แล้ว")
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(status_code=400, detail="Email นี้มีอยู่แล้ว")
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "message": "สร้างผู้ใช้สำเร็จ"}


@router.post("/users/{user_id}/toggle")
def toggle_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.is_active = not u.is_active
    db.commit()
    return {"id": u.id, "is_active": u.is_active}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if u.role == "admin":
        raise HTTPException(status_code=400, detail="ไม่สามารถลบ admin ได้")
    if u.id == admin.id:
        raise HTTPException(status_code=400, detail="ไม่สามารถลบตัวเองได้")
    db.delete(u)
    db.commit()
    return {"status": "deleted"}
