
from .ai import choose_alphabeta_move


def choose_move(board, depth=3, metrics=None):
    return choose_alphabeta_move(board, depth=depth, metrics=metrics)
