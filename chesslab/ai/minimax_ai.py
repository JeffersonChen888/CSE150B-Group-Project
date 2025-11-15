
from .ai import choose_minimax_move


def choose_move(board, depth=2, metrics=None):
    return choose_minimax_move(board, depth=depth, metrics=metrics)
