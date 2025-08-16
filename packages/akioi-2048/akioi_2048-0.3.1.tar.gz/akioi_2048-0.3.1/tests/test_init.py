"""Tests for :func:`akioi_2048.init`."""

import akioi_2048 as ak

ALLOWED = {-2, -1, 2, 4}


def flatten(board: list[list[int]]) -> list[int]:
    """Flatten a board into a single list.

    Returns:
        list[int]: A flattened list of all tile values.
    """
    return [c for row in board for c in row]


def test_init_board() -> None:
    """Initialize board with two tiles."""
    board = ak.init()
    flat = flatten(board)
    non_zero = [x for x in flat if x]
    assert len(flat) == 16
    assert len(non_zero) == 2
    assert all(x in ALLOWED for x in non_zero)
