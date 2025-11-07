
from . import random_agent, minimax_ai, alphabeta_ai

def one_ai_move(board, algo='AlphaBeta', depth=2, metrics=None):
    """Compute and apply exactly one AI move. Returns True if a move was made."""
    algo = (algo or 'AlphaBeta').lower()
    if metrics is None: metrics = {}
    if algo == 'random':
        move = random_agent.choose_move(board)
    elif algo == 'minimax':
        move, _ = minimax_ai.choose_move(board, depth=depth, metrics=metrics)
    else:
        move, _ = alphabeta_ai.choose_move(board, depth=depth, metrics=metrics)
    if move is None:
        return False
    board.make(move)
    return True
