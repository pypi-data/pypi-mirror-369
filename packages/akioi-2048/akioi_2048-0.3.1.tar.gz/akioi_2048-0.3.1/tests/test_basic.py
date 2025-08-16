"""Basic smoke tests for :func:`akioi_2048.step`."""

import akioi_2048 as ak

BOARD_SIZE = 4
VALID_STATES = (-1, 0, 1)


def test_step_smoke() -> None:
    """Initialize a board and perform a simple step."""
    board = ak.init()
    new_board, delta, msg = ak.step(board, 0)
    assert len(new_board) == BOARD_SIZE
    assert all(len(r) == BOARD_SIZE for r in new_board)
    assert isinstance(delta, int)
    assert msg in VALID_STATES
