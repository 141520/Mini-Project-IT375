from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import BoardGame, Conversation, Message, User
from schemas.chat import ChatRequest, ChatResponse, MessageOut, ConversationOut, RateRequest
from auth import get_current_user
from services import rag_service

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def ask(req: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    game = db.get(BoardGame, req.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not game.is_indexed:
        raise HTTPException(status_code=400, detail="Game rulebook is not yet indexed")

    # find or create conversation
    if req.conversation_id:
        conv = db.get(Conversation, req.conversation_id)
        if not conv or conv.user_id != user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = Conversation(user_id=user.id, game_id=game.id, title=req.question[:60])
        db.add(conv)
        db.commit()
        db.refresh(conv)

    db.add(Message(conversation_id=conv.id, role="user", content=req.question))
    db.commit()

    result = rag_service.answer_question(game.id, game.name, req.question)
    msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=result["answer"],
        citations=result["citations_json"],
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return ChatResponse(
        conversation_id=conv.id,
        message_id=msg.id,
        answer=result["answer"],
        citations=result["citations"],
    )


@router.post("/multi")
def ask_multi(req: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Search across ALL indexed games. Picks the game with the strongest hit."""
    from services import vector_store
    games = db.query(BoardGame).filter(BoardGame.is_indexed == True).all()
    if not games:
        raise HTTPException(status_code=400, detail="ยังไม่มีเกมที่ index แล้ว")

    best_game = None
    best_hits = []
    best_score = -1.0
    for g in games:
        hits = vector_store.search(g.id, req.question, top_k=4)
        if not hits:
            continue
        top_score = hits[0].get("score", 0.0)
        if top_score > best_score:
            best_score = top_score
            best_game = g
            best_hits = hits

    if not best_game:
        return {"answer": "ไม่พบข้อมูลในคู่มือเกมใด ๆ", "game": None, "citations": []}

    result = rag_service.generate_answer(best_game.name, req.question, best_hits)
    return {
        "answer": result,
        "game": {"id": best_game.id, "name": best_game.name, "image": best_game.image},
        "citations": [{"page": h["page"], "snippet": h["text"][:150]} for h in best_hits],
        "score": best_score,
    }


@router.get("/conversations", response_model=List[ConversationOut])
def list_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.is_pinned.desc(), Conversation.created_at.desc())
        .all()
    )


@router.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.get(Conversation, conv_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"status": "deleted"}


@router.post("/conversations/{conv_id}/pin")
def pin_conversation(conv_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.get(Conversation, conv_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.is_pinned = not conv.is_pinned
    db.commit()
    return {"is_pinned": conv.is_pinned}


@router.get("/conversations/{conv_id}/messages", response_model=List[MessageOut])
def get_messages(conv_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.get(Conversation, conv_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc())
        .all()
    )


@router.post("/messages/{msg_id}/rate")
def rate_message(msg_id: int, req: RateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = db.get(Message, msg_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    conv = db.get(Conversation, msg.conversation_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    msg.rating = max(-1, min(1, req.rating))
    db.commit()
    return {"status": "ok", "rating": msg.rating}
