# Team Members

| Name           | PID       | Roles                                            |
| :------------- | :-------- | :----------------------------------------------- |
| Angela Shen    | A18083528 | Writing contributor + planned eval improvement   |
| Fong Yu Lin    | A18496379 | Algorithm design & Optimization                  |
| Pranav Prabu   | A17424120 | Alternate algorithm development                  |
| Jefferson Chen | A18137549 | Implemented Basic Minmax and Alphabeta algorithm |

# Abstract

We implemented a basic evaluation function in conjunction with standard minimax and alpha–beta pruning algorithms, and we analyzed their behavior across a variety of game states. The minimax and alpha–beta routines closely follow the formulations taught in class, including recursive value propagation, terminal-state handling, and pruning of subtrees that cannot influence the optimal decision. Our primary design decision centered on constructing an evaluation function capable of capturing both positional features and phase-dependent strategy. To achieve this, we employed a piece-square table methodology, assigning values to each piece type based on its location on the board. This reflects the intuition that different positions confer different levels of mobility, control, and tactical opportunity. For instance, knights and queens receive elevated scores in central squares, where their movement options and influence over the board increase significantly. The king uses two distinct piece-square tables to account for the shift in priorities between the midgame and endgame: in earlier phases, its safety on the back rank is prioritized, while in the endgame, mobility and centralization become more valuable. Incorporating these positional and phase-based considerations allows the evaluation function to better approximate strategic reasoning and produce more consistent move assessments across varying game contexts.

# Introduction

## Milestone 1
After running initial tests, we observed that the agent’s move quality was noticeably suboptimal, indicating that our baseline evaluation function was not sufficiently informative. Because the evaluation function is the primary component that shapes the agent’s strategic behavior, we focused on refining it to enable more accurate position assessments. Our intuition was that different pieces gain meaningful advantages from specific board locations, and that capturing this positional nuance would improve decision quality. To incorporate this, we transitioned to a piece-square table approach that assigns positional bonuses and penalties for each piece type. These tables encode standard strategic principles—for example, central squares improve the mobility and influence of knights and queens, while edge squares tend to constrain them. We also recognized that the king’s priorities shift dramatically between phases of the game: during the opening and middlegame, safety and castling structures are paramount, whereas in the endgame, the king becomes an active piece. To model this behavior, we constructed two separate king tables corresponding to these phases.

Although this enhanced evaluation function produced a noticeably “smarter” agent, it also increased computational overhead. Decision times rose from roughly 1,000ms to approximately 9,000ms at depth 3, prompting us to shift our attention toward optimizing the alpha–beta pruning process. In the unoptimized implementation, moves were explored in essentially random order, which limited pruning effectiveness; encountering a poor move first forces the search to evaluate large portions of the tree, similar to plain minimax. To address this, we introduced move ordering. We developed a lightweight scoring heuristic, `score_move`, that generates a preliminary estimate of each move’s promise (e.g., capturing a high-value piece is prioritized, while non-impactful pawn moves are deprioritized). Before entering the alpha–beta search loop, we sort moves according to these scores so that stronger candidates are evaluated earlier. This significantly increases pruning opportunities and reduces unnecessary search. With this adjustment, decision time improved to approximately 4,000ms, effectively balancing strategic quality with computational efficiency.

P.S.: The initial piece-square bonus and penalty tables were generated using Gemini as a starting reference.

## Milestone 2

As to satisfy the requirement for milestone 2, we implemented the IDS for trying different depth and yeild with the best move out of depth from 1 to 50.

After knowing our team's AI did really bad in the tournament, we found that the issue is mainly about the long decision making time causing timeout and can't make proper moves. In order to fix this, we found some algorithms to improve our alpha-beta effiency in this website: https://rustic-chess.org/search/ordering/mvv_lva.html. We didn't know how exactly can we improve our AI so we consulted GPT and it introduced us to the Transposition Tables for improving effiency and quick heuristic for move ordering with MVV-LVA. We got more details information about these two algorithms in the website and implemented into our AI. Moreover, we implemented the Quiescence Search function which continue search until a 'quiet' position is found, and only considers captures and promotions. This function helps us get a more accurate evaluation by continuing the search until the board reaches a stable state. It prevents the AI from making mistakes by stopping the lookahead just before a recapture happens.

As a result, we have taken the lead in the sprint, blitz, rapid, classical tournaments.

## Questions we consulted GPT

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

**Prompt:** Is there a way to get available moves at depth 0? I think my AI currently stops abruptly at depth=0 and can't see the available at depth 0.

**Gemini:**

```
Yes! You can add a Quiescence Search: It can be a function inside choose_alphabeta_move. When the main search reaches depth=0, instead of stopping immediately, it continues searching only capture moves. This prevents the "Horizon Effect" (e.g., stopping the search right before you get your Queen captured back).

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
To use it:
if current_depth == 0:
            # Drop into Quiescence Search instead of raw evaluate
            return quiescence(board, alpha, beta, is_maximizing), None
```

**Prompt:** My AI is taking too long to make decision on making steps. How to increase its speed but continue select great moves?

**Gemini:**

```
To increase your AI's speed without sacrificing intelligence, we need to address two major performance bottlenecks in your current code:

Expensive Evaluation: Your evaluate function calculates len(board.legal_moves()). This is extremely slow because it requires generating and validating every move. Doing this at every leaf node paralyzes the search.

Redundant Calculations: Your Iterative Deepening (IDS) in choose_move recalculates the entire tree from scratch for every depth level. We need a Transposition Table (TT) to remember positions we've already seen.

Here is the optimized code. Replace the corresponding sections in your ai.py.

1. Optimize evaluate
Change: Remove the mobility calculation (the legal_moves part). The material scores and Piece-Square Tables are sufficient for a strong bot, and this single change will likely make your AI 10x-50x faster.

To increase your AI's speed without sacrificing intelligence, we need to address two major performance bottlenecks in your current code:

Expensive Evaluation: Your evaluate function calculates len(board.legal_moves()). This is extremely slow because it requires generating and validating every move. Doing this at every leaf node paralyzes the search.

Redundant Calculations: Your Iterative Deepening (IDS) in choose_move recalculates the entire tree from scratch for every depth level. We need a Transposition Table (TT) to remember positions we've already seen.

Here is the optimized code. Replace the corresponding sections in your ai.py.

1. Optimize evaluate
Change: Remove the mobility calculation (the legal_moves part). The material scores and Piece-Square Tables are sufficient for a strong bot, and this single change will likely make your AI 10x-50x faster.

2. Implement Transposition Table in choose_alphabeta_move
This allows the AI to store results. When choose_move runs depth 4, it can instantly look up results from depth 3 stored in the dictionary.

3. Update choose_move (Iterative Deepening)
You should clear the global TRANSPOSITION_TABLE occasionally (e.g., at the start of a turn) so it doesn't consume all your memory, though keeping it can help if the game state is similar. For this assignment, clearing it at the start of choose_move is safest.
```

**Prompt:** Are there ways to make alpha beta pruning more efficient?

**Claude:**

```
Yes, there are several techniques to make alpha-beta pruning more efficient! MVV-LVA (Most Valuable Victim - Least Valuable Attacker) is one of them. Here are the main optimization techniques:

## Move Ordering Techniques

**MVV-LVA (Most Valuable Victim - Least Valuable Attacker)**
- Prioritizes captures by evaluating the victim's value minus the attacker's value
- Example: Queen takes pawn is examined before pawn takes queen
- Dramatically improves cutoff rates in tactical positions

**Other move ordering heuristics:**
- **Killer moves**: Moves that caused cutoffs at the same depth in sibling nodes
- **History heuristic**: Tracks which moves historically caused cutoffs
- **PV (Principal Variation) moves**: Prioritize the best move from the previous search iteration
- **Hash move**: The best move stored in the transposition table for this position

## Transposition Tables
Store previously evaluated positions to avoid re-computing them. This is especially powerful in chess where the same position can be reached through different move orders.

## Iterative Deepening
Search to depth 1, then 2, then 3, etc. While this seems wasteful, it actually improves efficiency because:
- Earlier shallow searches inform move ordering for deeper searches
- Better move ordering means more cutoffs

## Aspiration Windows
Instead of searching with (-∞, +∞) bounds, use a narrow window around the expected score from a previous search. If the search fails, re-search with wider windows.

## Null Move Pruning
Give the opponent a free move. If you're still winning after giving them this advantage, you can safely prune this branch in many cases.

The combination of these techniques can reduce the effective branching factor from around 35 (in chess) down to 6 or less, making searches exponentially faster!
```
