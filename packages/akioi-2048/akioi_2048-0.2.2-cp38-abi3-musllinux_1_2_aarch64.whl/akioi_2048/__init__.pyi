from typing import List, Tuple

def step(board: List[List[int]], direction: int) -> Tuple[List[List[int]], int, int]:
    """
    Execute a move and (if successful) randomly generate a new tile.

    :param list[list[int]] board:
        4×4 board matrix.
        * **Positive values** → Normal value tiles (2, 4, 8, …)
        * **Negative values** → Multiplier tiles  -1=×1, -2=×2, -4=×4; absolute value is the multiplier.

    :param int dir:
        Move direction:
        * `0` = **Down**  ↓
        * `1` = **Right** →
        * `2` = **Up**    ↑
        * `3` = **Left**  ←

    :returns: *(new_board, delta_score, msg)*
        * **new_board** `list[list[int]]` Board after the move
        * **delta_score** `int` Score gained/lost from merges this move
        * **msg** `int` Status flag
            * `1`  → A `65536` tile was created  → **Victory**
            * `-1` → No possible moves in any direction → **Game Over**
            * `0`  → Continue playing

    :note:
        If the move is invalid (board unchanged),
        **no new tile is generated**, `delta_score = 0`, and `msg = 0`.
    """
    pass

def init() -> List[List[int]]:
    """
    Init a new board

    :returns: *new_board*
        * **new_board** `list[list[int]]` A new board
    """
    pass
