from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    X_WON = "x_won"
    O_WON = "o_won"
    DRAW = "draw"

class PlayerSymbol(str, Enum):
    X = "X"
    O = "O"

class GameMove(BaseModel):
    position: int = Field(..., ge=0, le=8)
    symbol: PlayerSymbol

class GameState(BaseModel):
    board: List[Optional[str]] = Field(default_factory=lambda: [None] * 9)
    current_player: PlayerSymbol
    status: GameStatus

class Game(BaseModel):
    id: int
    player_x_id: int
    player_o_id: int
    current_player: PlayerSymbol
    board: List[Optional[str]]
    status: GameStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GameCreate(BaseModel):
    player_o_id: int = Field(..., description="ID of the player who will play as O")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
