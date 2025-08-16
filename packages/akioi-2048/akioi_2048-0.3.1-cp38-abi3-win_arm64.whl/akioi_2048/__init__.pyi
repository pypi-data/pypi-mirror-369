"""Type hints for :mod:`akioi_2048`."""

def step(
    board: list[list[int]],
    direction: int,
) -> tuple[list[list[int]], int, int]:
    """Apply one move.

    If the board changes, a new tile appears in a random empty cell.

    Args:
        board: 4x4 game board. Positive numbers are normal tiles (2, 4, 8,
            ...). Negative numbers are multipliers: -1=x1, -2=x2, -4=x4
            (absolute value is the multiplier).
        direction: Move direction (0=Down ↓, 1=Right →, 2=Up ↑, 3=Left ←).

    Returns:
        tuple[list[list[int]], int, int]: ``(new_board, delta_score, state)``.

    The tuple contains:
        * ``new_board``: Board after the move.
        * ``delta_score``: Score gained or lost from merges.
        * ``state``: Game state flag.
            * ``1`` indicates a ``65536`` tile was created (Victory).
            * ``-1`` indicates no legal moves remain (Game Over).
            * ``0`` indicates the game continues.

    Note:
        If the board does not change, no tile is spawned,
        ``delta_score = 0``, and ``state = 0``.
    """

def init() -> list[list[int]]:
    """Create a new board with two starting tiles.

    Returns:
        list[list[int]]: Fresh board ready for play.
    """
