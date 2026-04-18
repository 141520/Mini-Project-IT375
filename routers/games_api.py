from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import BoardGame, Favorite, User
from schemas.game import GameOut
from auth import get_current_user

router = APIRouter(prefix="/api/v1/games", tags=["games"])


@router.get("", response_model=List[GameOut])
def list_games(search: str = "", db: Session = Depends(get_db)):
    q = db.query(BoardGame)
    if search:
        q = q.filter(BoardGame.name.like(f"%{search}%"))
    return q.order_by(BoardGame.created_at.desc()).all()


@router.get("/{game_id}", response_model=GameOut)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = db.get(BoardGame, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("/{game_id}/favorite")
def toggle_favorite(game_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(BoardGame, game_id):
        raise HTTPException(status_code=404, detail="Game not found")
    fav = db.query(Favorite).filter_by(user_id=user.id, game_id=game_id).first()
    if fav:
        db.delete(fav)
        db.commit()
        return {"favorited": False}
    db.add(Favorite(user_id=user.id, game_id=game_id))
    db.commit()
    return {"favorited": True}


@router.get("/favorites/mine", response_model=List[GameOut])
def my_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favs = db.query(Favorite).filter_by(user_id=user.id).all()
    return [db.get(BoardGame, f.game_id) for f in favs if db.get(BoardGame, f.game_id)]
