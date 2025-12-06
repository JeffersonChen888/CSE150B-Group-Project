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

TRANSPOSITION_TABLE = {}

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
    3. Check penalties/bonuses
    """
    # Check for game checkmate/stalemate immediately
    outcome = board.outcome()
    if outcome:
        if outcome[0] == 'checkmate':
            return 1000000 if outcome[1] == 'w' else -1000000
        else:
            return 0 # Stalemate

    score = 0
    white_material = 0
    black_material = 0
    
    PIECE_TABLES = {
        'P': PAWN_TABLE, 'N': KNIGHT_TABLE, 'B': BISHOP_TABLE,
        'R': ROOK_TABLE, 'Q': QUEEN_TABLE
    }

    # Efficient board scan
    for r in range(8):
        for c in range(8):
            piece = board.piece_at(r, c)
            if not piece:
                continue

            color = piece[0]
            piece_type = piece[1]
            
            # lookup material
            material_value = PIECE_VALUES.get(piece_type, 0)
            
            # lookup position
            positional_score = 0
            if piece_type in PIECE_TABLES:
                if color == 'w':
                    positional_score = PIECE_TABLES[piece_type][r][c]
                else:
                    positional_score = PIECE_TABLES[piece_type][7 - r][c]
                
                if color == 'w': white_material += material_value
                else: black_material += material_value

            elif piece_type == 'K':
                # Determine game phase based on material
                total_material = (white_material + black_material) / 100
                is_endgame = total_material < 20
                
                table = KING_END_GAME_TABLE if is_endgame else KING_MIDDLE_GAME_TABLE
                if color == 'w':
                    positional_score = table[r][c]
                else:
                    positional_score = table[7 - r][c]

            # Accumulate score
            if color == 'w':
                score += material_value + positional_score
            else:
                score -= (material_value + positional_score)
    
    # Check Bonuses/Penalties
    if board.is_check('w'):
        score -= 50
    if board.is_check('b'):
        score += 50

    return score

def choose_minimax_move(board, depth=2, metrics=None):
    """
    Pick a move for the current player using minimax (no pruning).
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
    
    # Flags for Transposition Table
    EXACT = 0
    LOWERBOUND = 1
    UPPERBOUND = 2

    def score_move(board, move):
        # Quick heuristic for move ordering
        start, end, promote = move
        victim = board.piece_at(end[0], end[1])
        attacker = board.piece_at(start[0], start[1])
        score = 0
        if victim:
            # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
            score = 100 * PIECE_VALUES.get(victim[1], 0) - PIECE_VALUES.get(attacker[1], 0)
        if promote == 'Q':
            score += 900
        return score

    def quiescence(board, alpha, beta, is_maximizing):
        """
        Continue search until a 'quiet' position is found.
        Only considers captures and promotions.
        """
        nodes_visited[0] += 1
        stand_pat = evaluate(board)
        
        # Fail-hard beta cutoff
        if is_maximizing:
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat

        # Get all legal moves
        legal_moves = board.legal_moves()
        
        # Filter for "Loud" moves: Captures or Promotions
        loud_moves = []
        for move in legal_moves:
            dst_r, dst_c = move.dst
            # Check if there is a piece at destination (Capture) OR if it is a promotion
            if board.piece_at(dst_r, dst_c) is not None or move.promote is not None:
                loud_moves.append(move)

        if not loud_moves:
            return stand_pat

        # Order captures by MVV-LVA
        loud_moves.sort(key=lambda m: score_move(board, m), reverse=True)

        if is_maximizing:
            for move in loud_moves:
                new_board = board.clone()
                new_board.make(move)
                score = quiescence(new_board, alpha, beta, False)
                
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
            return alpha
        else:
            for move in loud_moves:
                new_board = board.clone()
                new_board.make(move)
                score = quiescence(new_board, alpha, beta, True)
                
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score
            return beta

    def alphabeta(board, current_depth, alpha, beta, is_maximizing):
        nodes_visited[0] += 1
        
        # Transposition Table Lookup
        # Create a hashable tuple representation of the board + turn
        board_key = (
            tuple(tuple(row) for row in board.board),
            board.turn
        )
        
        tt_entry = TRANSPOSITION_TABLE.get(board_key)
        
        if tt_entry and tt_entry[0] >= current_depth:
            tt_depth, tt_value, tt_flag, tt_move = tt_entry
            if tt_flag == EXACT:
                return tt_value, tt_move
            elif tt_flag == LOWERBOUND:
                alpha = max(alpha, tt_value)
            elif tt_flag == UPPERBOUND:
                beta = min(beta, tt_value)
            
            if alpha >= beta:
                return tt_value, tt_move

        outcome = board.outcome()
        if outcome:
            if outcome[0] == 'checkmate':
                # Prefer shorter mates
                score = 1000000 + current_depth if outcome[1] == 'w' else -1000000 - current_depth
                return score, None
            return 0, None

        if current_depth == 0:
            # Drop into Quiescence Search instead of raw evaluate
            return quiescence(board, alpha, beta, is_maximizing), None

        # Move Ordering
        legal_moves = board.legal_moves()
        if not legal_moves:
            return evaluate(board), None

        # Try the TT move first (pv_move), then captures, then rest
        pv_move = None
        if tt_entry:
            pv_move = tt_entry[3]
            
        def move_sorter(m):
            if m == pv_move: return 1000000
            return score_move(board, m)
            
        sorted_moves = sorted(legal_moves, key=move_sorter, reverse=True)

        best_move_in_node = None
        if is_maximizing:
            value = float('-inf')
            for move in sorted_moves:
                new_board = board.clone()
                new_board.make(move)
                new_val, _ = alphabeta(new_board, current_depth - 1, alpha, beta, False)
                
                if new_val > value:
                    value = new_val
                    best_move_in_node = move
                
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = float('inf')
            for move in sorted_moves:
                new_board = board.clone()
                new_board.make(move)
                new_val, _ = alphabeta(new_board, current_depth - 1, alpha, beta, True)
                
                if new_val < value:
                    value = new_val
                    best_move_in_node = move
                    
                beta = min(beta, value)
                if beta <= alpha:
                    break

        # Store in Transposition Table
        flag = EXACT
        if value <= alpha: flag = UPPERBOUND
        elif value >= beta: flag = LOWERBOUND
        
        TRANSPOSITION_TABLE[board_key] = (current_depth, value, flag, best_move_in_node)
        
        return value, best_move_in_node

    # Start the search from the root
    alpha = float('-inf')
    beta = float('inf')
    is_max = (board.turn == 'w')
    
    best_val, best_move = alphabeta(board, depth, alpha, beta, is_max)
    
    return best_move, nodes_visited[0]

def choose_move(board):
    """
    Pick a move using iterative deepening search (IDS).
    """
    global TRANSPOSITION_TABLE
    TRANSPOSITION_TABLE.clear()
    
    legal_moves = board.legal_moves()
    if not legal_moves:
        return

    yield legal_moves[0]
    
    for depth in range(1, 50):
        try:
            best_move, nodes = choose_alphabeta_move(board, depth=depth)
            
            if best_move:
                yield best_move
        except Exception:
            break