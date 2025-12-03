# ChessLab (Group Project Starter Code)

Self-contained chess GUI + AI assignment.

-   Rules: all standard moves **except** castling & en passant (omitted for clarity). Promotion->Queen.
-   GUI: click piece then destination. Modes: Human vs Human, Human vs AI, AI vs AI.
-   AI: You are required to implement any of the following: Random, Minimax, AlphaBeta (students implementations i.e. random/minimax/alphabeta, go in `chesslab/ai/ai.py`).
-   Student work happens exclusively in `chesslab/ai/ai.py`. When submitting to Gradescope, upload only that file (`ai.py`).

Stages: random, eval, minimax, alphabeta.

# Team Members

| Name           | PID       | Roles                           |
| :------------- | :-------- | :------------------------------ |
| Angela         |           |                                 |
| Fong Yu Lin    | A18496379 | Algorithm design & Optimization |
| Nav            |           |                                 |
| Jefferson Chen |           |                                 |

# Abstract

We implement a basic evaluate function, minimax, and alphabeta algorithms, and observe their performance. Minimax and alphabeta algorithms are the same as what we learned in class. For the evaluation function, we use a table based strategy, where we assign different values at each position for each kind of piece. This is because some positions are more optimal for a specific kind of piece, for example the knight and queen have higher values at the center of the table because their movement options greatly increase in the center of the board. Alternatively, the king, which has two position value tables for different stages of the game, wants to be at the bottom row at the start and middle of the game, since it is more likely there will be other pieces at the bottom rows to prevent checkmate, and then it can move to the middle of the board later in the game.

# Introduction

We then noticed that the result didn't go that well as the AI isn't making well enough moves. So, we thought of improving the algorithm for the evaluate function. We think that the evaluation is one of the main thing that can make our AI "smarter", meaning to make it take better moves. We thought of maybe the the pieces can have higher advantages when they're in certain positions. Therefore, we created tables for each piece with their bonus/penalty for it to know which piece should go where to get more advantage. And then we've also found out that the King piece has different strategies in different stage of the game (in middle game it needs to be safe, and in end game it needs to be active). We then create two type of tables for the King piece.

Moreover, now we have a "smarter" AI that makes better decisions, but it's now taking too long to make the decisions (from the original ~1,000ms to ~9,000ms now for depth=3). We moved our focus to optimizing the alphabeta algorithm. With original alphabeta algorithm, we were looking at moves in random order. If we get the worst move first, then we'll still have to search through everything just like minimax. So, we decided to improve the moving order and get the good looing "best" moves first and let the alphabeta pruning kicks in ealier. We added a helper function called `score_move` to look at one move and "guess" if that move is good (capturing Queen is good, moving pawn is boring). And then before the loop, we sort the scores that we got for the moves to let the "best" moves to be looped first. As the result, we successfully reduced the decision time to ~4,000ms.

P.S.: We asked Gemini for the bonus/penalty table for the evaluation.

**Prompt:** How can I let the AI to know which pieces to go where can get more advantages?

**Gemini:**

```
Add Piece-Square Tables (Positional Awareness)

This is the biggest "bang for your buck" improvement. A piece-square table is a 2D array (like the board) that gives a small bonus or penalty to a piece depending on where it is.

Example (Pawn): A pawn on the 7th rank (about to promote) is much more valuable than a pawn on the 2nd.

Example (Knight): A knight in the center (e.g., d4, e5) controls many squares and is worth more than a knight on the rim (e.g., a8, h1), which is "dim."

You would create a table for each piece type. For example, a simplified PAWN_TABLE might look like this (from White's perspective):

Python

# (Values are just for illustration)
PAWN_TABLE = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # Rank 8
    [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],  # Rank 7 (Promotion)
    [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],  # Rank 6
    [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],  # Rank 5
    [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],  # Rank 4 (Center)
    [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5], # Rank 3
    [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5], # Rank 2
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]   # Rank 1
]
In your evaluate loop, if you find a White Pawn at (r, c), you would add PIECE_VALUES['P'] + PAWN_TABLE[r][c] to the score. If you find a Black Pawn, you'd subtract PIECE_VALUES['P'] + PAWN_TABLE[7-r][c] (since the table is flipped for Black).
```
