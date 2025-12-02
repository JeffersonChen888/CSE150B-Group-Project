# ChessLab (Group Project)

Self-contained chess GUI and AI assignment for CSE 150B.

## Game Rules

Standard chess rules apply with the following simplifications:
- No castling
- No en passant
- Pawn promotion is to Queen only

These omissions keep the focus on search algorithms rather than edge-case move generation.

## GUI Usage

Run with `python -m chesslab` from the project root.

Click a piece, then click its destination square. Three play modes are available:
- Human vs Human
- Human vs AI
- AI vs AI

## Your Task

Implement your AI in `chesslab/ai/ai.py`. This is the only file you submit to Gradescope.

You must implement one or more of the following: Random, Minimax, or AlphaBeta search.

## Tournament

Your submissions will compete against each other in a class tournament. Here is what you need to know.

### How It Works

The tournament runs five rounds with increasing time limits per move:
- Sprint: ? seconds/move
- Blitz: ? seconds/move
- Rapid: ? seconds/move
- Classical: ? seconds/move
- Extended: ? seconds/move

Each team plays every other team twice per round (once as White, once as Black). Scoring follows standard chess conventions: 1 point for a win, 0.5 for a draw, 0 for a loss.

### Time Limits and Forfeits

Your AI must return a move before the time limit expires. If it does not, you forfeit that game. Your code does not receive the time limit as a parameter. Design your search to return reasonable moves quickly.

### Supported Function Signatures

The tournament checks for these functions in your `ai.py`, in this order:

1. `choose_move(board)` - Preferred. Can be a regular function or a generator.
2. `choose_alphabeta_move(board, depth, metrics)` - Legacy format, returns `(move, node_count)`.
3. `choose_minimax_move(board, depth, metrics)` - Legacy format, returns `(move, node_count)`.
4. `choose_random_move(board)` - Fallback.

The first function found is used for the tournament.

### Generator Pattern for Iterative Deepening

If you implement iterative deepening search (IDS -- (in progress, may not work perfectly yet!)), consider using a generator. This allows you to yield progressively better moves as you search deeper. The tournament will use the last move you yielded when time runs out.

```python
def choose_move(board):
    legal_moves = board.legal_moves()
    if not legal_moves:
        return

    # Yield a quick move immediately to avoid forfeit
    yield random.choice(legal_moves)

    # Search deeper and yield better moves
    for depth in range(1, 50):
        best_move = alphabeta_search(board, depth)
        if best_move:
            yield best_move
```

The key point: yield a move early. If time expires before you yield anything, you forfeit. The generator pattern gives you a safety net while still allowing deeper search when time permits.

### Example AI

See `chesslab/ai/ai_example.py` for a complete implementation demonstrating both the generator pattern and the legacy function signatures.

## Project Structure

```
chesslab/
    __init__.py
    __main__.py      # Entry point
    board.py         # Board representation and move generation
    gui.py           # Tkinter interface
    ai/
        __init__.py
        ai.py        # Your implementation goes here
        ai_example.py # Reference implementation
    common/
        profiling.py # Performance measurement utilities
```

## Running the Tournament Locally

Coming soon!:

```bash
# insert test example here

```

## Submission

Upload only `ai.py` to Gradescope. The autograder tests basic functionality. Tournament performance is evaluated separately.
