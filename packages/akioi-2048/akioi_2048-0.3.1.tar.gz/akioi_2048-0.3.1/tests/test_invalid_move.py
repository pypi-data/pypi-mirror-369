"""Tests for invalid moves."""

import akioi_2048 as ak


def test_invalid_move_triggers_failure() -> None:
    """A move that changes nothing and leaves no moves should fail."""
    board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    new_board, delta, msg = ak.step(board, 0)
    assert new_board == board
    assert delta == 0
    assert msg == -1


def test_invalid_move_no_failure() -> None:
    """Invalid move that does not trigger failure when other moves exist."""
    board = [
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    new_board, delta, msg = ak.step(board, 2)
    assert new_board == board
    assert delta == 0
    assert msg == 0
