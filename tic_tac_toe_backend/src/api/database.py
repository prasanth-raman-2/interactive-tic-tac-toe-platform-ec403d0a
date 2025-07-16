from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .models import GameStatus, PlayerSymbol

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player_x_id = Column(Integer, ForeignKey("users.id"))
    player_o_id = Column(Integer, ForeignKey("users.id"))
    current_player = Column(SQLEnum(PlayerSymbol))
    board = Column(ARRAY(String), default=[None] * 9)
    status = Column(SQLEnum(GameStatus))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    player_x = relationship("User", foreign_keys=[player_x_id])
    player_o = relationship("User", foreign_keys=[player_o_id])
