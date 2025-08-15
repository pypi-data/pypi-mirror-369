"""Type hints for :mod:`akioi_2048`."""

from typing import List, Tuple

def step(board: List[List[int]], direction: int) -> Tuple[List[List[int]], int, int]:
    """
    Apply one move. If the board changes, a new tile appears in a random empty cell.

    :param board: 4×4 game board.
        * Positive numbers are normal tiles (2, 4, 8, …)
        * Negative numbers are multipliers: -1=×1, -2=×2, -4=×4
          (absolute value is the multiplier)

    :param direction: Move direction (0=Down ↓, 1=Right →, 2=Up ↑, 3=Left ←)

    :returns: *(new_board, delta_score, state)*
        * **new_board** `list[list[int]]` Board after the move
        * **delta_score** `int` Score gained or lost from merges
        * **state** `int` Game state flag
            * `1`  → created a `65536` tile → **Victory**
            * `-1` → no legal moves remain → **Game Over**
            * `0`  → game continues

    :note: If the board does not change, no tile is spawned, ``delta_score = 0``,
        and ``state = 0``.
    """
    ...

def init() -> List[List[int]]:
    """
    Create a new board with two starting tiles.

    :returns: *new_board*
        * **new_board** `list[list[int]]` Fresh board ready for play
    """
    ...
