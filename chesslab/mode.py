
from typing import Literal

WHITE, BLACK = 'w','b'

def is_ai_turn(mode: str, turn: str, ai_side: Literal['w','b']='b') -> bool:
    if mode == 'AI vs AI':
        return True
    if mode == 'Human vs Human':
        return False
    # Human vs AI
    return turn == ai_side

def is_human_turn(mode: str, turn: str, human_side: Literal['w','b']='w') -> bool:
    if mode == 'Human vs Human':
        return True
    if mode == 'AI vs AI':
        return False
    # Human vs AI
    return turn == human_side
