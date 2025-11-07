"""
Core AI routines for ChessLab.

All of the student work for this assignment lives in this file. Implement the
functions below so that:
  * `evaluate` returns a heuristic score for the given board state.
  * `choose_minimax_move` picks a move via minimax search (no pruning).
  * `choose_alphabeta_move` picks a move via minimax with alpha-beta pruning.

The helper `choose_random_move` is provided for you.
"""

from __future__ import annotations

import random
from typing import Optional, Tuple

from ..common.profiling import Counter

MoveType = Tuple[Tuple[int, int], Tuple[int, int], Optional[str]]


def choose_random_move(board):
    """Return a uniformly random legal move or None if no moves exist."""
    legal = board.legal_moves()
    return random.choice(legal) if legal else None


def evaluate(board):
    """Return a heuristic score from White's perspective."""
    raise NotImplementedError("Implement your evaluation function in ai.py")


def choose_minimax_move(board, depth=2, metrics=None):
    """
    Pick a move for the current player using minimax (no pruning).

    Returns:
        (best_move, nodes_visited)
    """
    raise NotImplementedError("Implement minimax search in ai.py")


def choose_alphabeta_move(board, depth=3, metrics=None):
    """
    Pick a move for the current player using minimax with alpha-beta pruning.

    Returns:
        (best_move, nodes_visited)
    """
    raise NotImplementedError("Implement alpha-beta search in ai.py")
