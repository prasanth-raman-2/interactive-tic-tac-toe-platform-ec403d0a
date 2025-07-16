from typing import List, Optional
from .models import GameStatus, PlayerSymbol

def check_winner(board: List[Optional[str]]) -> Optional[str]:
    # Winning combinations
    lines = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
        (0, 4, 8), (2, 4, 6)  # Diagonals
    ]
    
    for start, mid, end in lines:
        if (board[start] and board[start] == board[mid] and 
            board[start] == board[end]):
            return board[start]
    return None

def is_board_full(board: List[Optional[str]]) -> bool:
    return all(cell is not None for cell in board)

def get_game_status(board: List[Optional[str]]) -> GameStatus:
    winner = check_winner(board)
    if winner == PlayerSymbol.X:
        return GameStatus.X_WON
    elif winner == PlayerSymbol.O:
        return GameStatus.O_WON
    elif is_board_full(board):
        return GameStatus.DRAW
    return GameStatus.IN_PROGRESS

def validate_move(board: List[Optional[str]], position: int, current_player: PlayerSymbol) -> bool:
    if not (0 <= position <= 8):
        return False
    if board[position] is not None:
        return False
    return True

def make_move(board: List[Optional[str]], position: int, symbol: PlayerSymbol) -> List[Optional[str]]:
    new_board = board.copy()
    new_board[position] = symbol
    return new_board

def get_next_player(current_player: PlayerSymbol) -> PlayerSymbol:
    return PlayerSymbol.O if current_player == PlayerSymbol.X else PlayerSymbol.X
