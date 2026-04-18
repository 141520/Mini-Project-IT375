from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GameBase(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "th"
    category: Optional[str] = None


class GameCreate(GameBase):
    pass


class GameOut(GameBase):
    id: int
    image: Optional[str] = None
    pdf_path: Optional[str] = None
    is_indexed: bool
    total_pages: int
    created_at: datetime

    class Config:
        from_attributes = True
