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


# Piece values
PIECE_VALUES = {
    'P': 100,  # Pawn
    'N': 320,  # Knight
    'B': 330,  # Bishop
    'R': 500,  # Rook
    'Q': 900,  # Queen
    'K': 20000 # King (high value for checkmate calculation)
}

# Black's score is found by flipping the row: table[7 - r][c]

PAWN_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

ROOK_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

# King table for middle game
KING_MIDDLE_GAME_TABLE = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [ 10, 10,  0,  0,  0,  0, 10, 10],
    [ 10, 10,  0,  0,  0,  0, 10, 10]
]

KING_END_GAME_TABLE = [
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,  0,  0,-10,-20,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-30,  0,  0,  0,  0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50]
]

def evaluate(board):
    """
    Return a heuristic score from White's perspective.
    This improved version includes:
    1. Material count (using centipawns)
    2. Piece-Square Tables for positional awareness
    3. Mobility score for the current player
    """
    # Check for game checkmate
    outcome = board.outcome()
    if outcome:
        if outcome[0] == 'checkmate':
            return 1000000 if outcome[1] == 'w' else -1000000
        else:
            return 0

    score = 0
    white_material = 0
    black_material = 0
    
    PIECE_TABLES = {
        'P': PAWN_TABLE,
        'N': KNIGHT_TABLE,
        'B': BISHOP_TABLE,
        'R': ROOK_TABLE,
        'Q': QUEEN_TABLE
    }

    for r in range(8):
        for c in range(8):
            piece = board.piece_at(r, c)
            if not piece:
                continue

            color = piece[0]
            piece_type = piece[1]
            
            material_value = PIECE_VALUES.get(piece_type, 0)
            positional_score = 0

            if piece_type in PIECE_TABLES:
                if color == 'w':
                    positional_score = PIECE_TABLES[piece_type][r][c]
                    white_material += material_value
                else:
                    positional_score = PIECE_TABLES[piece_type][7 - r][c]
                    black_material += material_value
            
            elif piece_type == 'K':
                total_material = (white_material + black_material) / 100
                
                # A simple heuristic: < 20 material points = endgame
                if total_material < 20: 
                    if color == 'w':
                        positional_score = KING_END_GAME_TABLE[r][c]
                    else:
                        positional_score = KING_END_GAME_TABLE[7 - r][c]
                else: # Middle game
                    if color == 'w':
                        positional_score = KING_MIDDLE_GAME_TABLE[r][c]
                    else:
                        positional_score = KING_MIDDLE_GAME_TABLE[7 - r][c]

            if color == 'w':
                score += material_value + positional_score
            else:
                score -= (material_value + positional_score)

    mobility_weight = 10
    num_legal_moves = len(board.legal_moves())

    if board.turn == 'w':
        score += num_legal_moves * mobility_weight
    else:
        score -= num_legal_moves * mobility_weight

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
    
    def score_move(board, move):
        start_sq, end_sq, promotion = move
        
        piece = board.piece_at(start_sq[0], start_sq[1])
        if not piece:
            return 0
            
        piece_type = piece[1]
        captured_piece = board.piece_at(end_sq[0], end_sq[1])
        
        score = 0

        if captured_piece:
            attacker_val = PIECE_VALUES.get(piece_type, 0)
            victim_val = PIECE_VALUES.get(captured_piece[1], 0)
            score = 1000 + (victim_val - attacker_val)

        if promotion == 'Q':
            score += PIECE_VALUES['Q']
        
        return score

    def alphabeta(board, depth, alpha, beta, is_maximizing):
        nodes_visited[0] += 1

        outcome = board.outcome()
        if outcome:
            if outcome[0] == 'checkmate':
                return 1000000 if outcome[1] == 'w' else -1000000
            else:
                return 0

        if depth == 0:
            return evaluate(board)

        legal_moves = board.legal_moves()
        if not legal_moves:
            return evaluate(board)
        
        sorted_moves = sorted(legal_moves, key=lambda m: score_move(board, m), reverse=True)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in sorted_moves:
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
            for move in sorted_moves:
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

    sorted_moves = sorted(legal_moves, key=lambda m: score_move(board, m), reverse=True)
    
    best_move = None
    best_value = float('-inf') if is_maximizing else float('inf')
    alpha = float('-inf')
    beta = float('inf')

    for move in sorted_moves:
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

def choose_move(board):
    """
    Pick a move using iterative deepening search (IDS).

    This is a generator function that yields progressively better moves
    as the search deepens. The tournament will use the last move yielded
    before the time limit expires.

    IMPORTANT: Yield a move early to avoid forfeit! If no move is yielded
    before time runs out, you lose the game.

    Example implementation:
        def choose_move(board):
            legal_moves = board.legal_moves()
            if not legal_moves:
                return

            # Yield a quick move immediately to avoid forfeit
            yield legal_moves[0]

            # Search deeper and yield better moves
            for depth in range(1, 50):
                best_move = alphabeta_search(board, depth)
                if best_move:
                    yield best_move

    Yields:
        Move objects, progressively better as search deepens
    """
    raise NotImplementedError("Implement iterative deepening search in ai.py")
    yield  # Makes this a generator function
