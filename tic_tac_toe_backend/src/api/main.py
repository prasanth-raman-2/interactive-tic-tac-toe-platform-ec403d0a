from datetime import timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, database, auth, game_logic
from .database_connection import engine

# Create database tables
database.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tic Tac Toe API",
    description="Backend API for the Tic Tac Toe game",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public endpoints
@app.post("/register", response_model=models.User)
def register_user(user: models.UserCreate, db: Session = Depends(auth.get_db)):
    """Register a new user"""
    db_user = db.query(database.User).filter(
        database.User.email == user.email
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = database.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(auth.get_db)
):
    """Login to get access token"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoints
@app.post("/games", response_model=models.Game)
async def create_game(
    game_create: models.GameCreate,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(auth.get_db)
):
    """Create a new game"""
    opponent = db.query(database.User).filter(
        database.User.id == game_create.player_o_id
    ).first()
    if not opponent:
        raise HTTPException(status_code=404, detail="Opponent not found")

    game = database.Game(
        player_x_id=current_user.id,
        player_o_id=opponent.id,
        current_player=models.PlayerSymbol.X,
        board=[None] * 9,
        status=models.GameStatus.IN_PROGRESS
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

@app.get("/games", response_model=List[models.Game])
async def list_games(
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(auth.get_db)
):
    """List all games for the current user"""
    games = db.query(database.Game).filter(
        (database.Game.player_x_id == current_user.id) |
        (database.Game.player_o_id == current_user.id)
    ).all()
    return games

@app.get("/games/{game_id}", response_model=models.Game)
async def get_game(
    game_id: int,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(auth.get_db)
):
    """Get a specific game"""
    game = db.query(database.Game).filter(database.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.player_x_id != current_user.id and game.player_o_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this game")
    return game

@app.post("/games/{game_id}/move", response_model=models.Game)
async def make_move(
    game_id: int,
    move: models.GameMove,
    current_user: database.User = Depends(auth.get_current_user),
    db: Session = Depends(auth.get_db)
):
    """Make a move in the game"""
    game = db.query(database.Game).filter(database.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Validate it's the player's turn
    player_symbol = (models.PlayerSymbol.X if game.player_x_id == current_user.id
                    else models.PlayerSymbol.O)
    if player_symbol != game.current_player:
        raise HTTPException(status_code=400, detail="Not your turn")
    
    if not game_logic.validate_move(game.board, move.position, game.current_player):
        raise HTTPException(status_code=400, detail="Invalid move")
    
    # Make the move
    game.board = game_logic.make_move(game.board, move.position, player_symbol)
    game.status = game_logic.get_game_status(game.board)
    
    if game.status == models.GameStatus.IN_PROGRESS:
        game.current_player = game_logic.get_next_player(game.current_player)
    
    db.commit()
    db.refresh(game)
    return game

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
