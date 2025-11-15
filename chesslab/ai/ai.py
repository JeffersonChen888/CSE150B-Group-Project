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
    # Piece values
    PIECE_VALUES = {
        'P': 1,
        'N': 3,
        'B': 3,
        'R': 5,
        'Q': 9,
        'K': 1000
    }

    score = 0
    outcome = board.outcome()

    if outcome:
        if outcome[0] == 'checkmate':
            if outcome[1] == 'w':
                return 10000
            else:
                return -10000
        else:
            return 0

    for r in range(8):
        for c in range(8):
            piece = board.piece_at(r, c)
            if piece:
                color = piece[0]
                piece_type = piece[1]
                value = PIECE_VALUES.get(piece_type, 0)

                if color == 'w':
                    score += value
                else:
                    score -= value

    return score


def choose_minimax_move(board, depth=2, metrics=None):
    """
    Pick a move for the current player using minimax (no pruning).

    Returns:
        (best_move, nodes_visited)
    """
    nodes_visited = [0]  

    def minimax(board, depth, is_maximizing):
        nodes_visited[0] += 1

        outcome = board.outcome()
        if outcome:
            if outcome[0] == 'checkmate':
                if outcome[1] == 'w':
                    return 10000  
                else:
                    return -10000  
            else:
                return 0  

        if depth == 0:
            return evaluate(board)

        legal_moves = board.legal_moves()
        if not legal_moves:
            return evaluate(board)

        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                new_board = board.clone()
                new_board.make(move)
                eval_score = minimax(new_board, depth - 1, False)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                new_board = board.clone()
                new_board.make(move)
                eval_score = minimax(new_board, depth - 1, True)
                min_eval = min(min_eval, eval_score)
            return min_eval

    is_maximizing = (board.turn == 'w')
    legal_moves = board.legal_moves()

    if not legal_moves:
        return None, 0

    best_move = None
    best_value = float('-inf') if is_maximizing else float('inf')

    for move in legal_moves:
        new_board = board.clone()
        new_board.make(move)
        move_value = minimax(new_board, depth - 1, not is_maximizing)

        if is_maximizing:
            if move_value > best_value:
                best_value = move_value
                best_move = move
        else:
            if move_value < best_value:
                best_value = move_value
                best_move = move

    return best_move, nodes_visited[0]


def choose_alphabeta_move(board, depth=3, metrics=None):
    """
    Pick a move for the current player using minimax with alpha-beta pruning.

    Returns:
        (best_move, nodes_visited)
    """
    nodes_visited = [0]

    def alphabeta(board, depth, alpha, beta, is_maximizing):
        nodes_visited[0] += 1

        outcome = board.outcome()
        if outcome:
            if outcome[0] == 'checkmate':
                if outcome[1] == 'w':
                    return 10000  
                else:
                    return -10000  
            else:
                return 0  

        if depth == 0:
            return evaluate(board)

        legal_moves = board.legal_moves()
        if not legal_moves:
            return evaluate(board)

        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                new_board = board.clone()
                new_board.make(move)
                eval_score = alphabeta(
                    new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                new_board = board.clone()
                new_board.make(move)
                eval_score = alphabeta(
                    new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break 
            return min_eval

    is_maximizing = (board.turn == 'w')
    legal_moves = board.legal_moves()

    if not legal_moves:
        return None, 0

    best_move = None
    best_value = float('-inf') if is_maximizing else float('inf')
    alpha = float('-inf')
    beta = float('inf')

    for move in legal_moves:
        new_board = board.clone()
        new_board.make(move)
        move_value = alphabeta(
            new_board, depth - 1, alpha, beta, not is_maximizing)

        if is_maximizing:
            if move_value > best_value:
                best_value = move_value
                best_move = move
            alpha = max(alpha, move_value)
        else:
            if move_value < best_value:
                best_value = move_value
                best_move = move
            beta = min(beta, move_value)

    return best_move, nodes_visited[0]
