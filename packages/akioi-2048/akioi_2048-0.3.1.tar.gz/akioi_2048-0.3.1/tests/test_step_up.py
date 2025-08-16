"""Tests for upward moves and merges."""

import akioi_2048 as ak


def test_up_number_merges_and_positive_score() -> None:
    """Numbers merge when moving up and increase the score."""
    board = [
        [4, 0, 0, 0],
        [4, 0, 0, 0],
        [2, 0, 0, 0],
        [2, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 2)
    assert new_board[0][0] == 8
    assert new_board[1][0] == 4
    assert delta == 12


def test_up_multiplier_merges_and_negative_score() -> None:
    """Multipliers merge when moving up and decrease the score."""
    board = [
        [-2, 0, 0, 0],
        [-2, 0, 0, 0],
        [-1, 0, 0, 0],
        [-1, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 2)
    assert new_board[0][0] == -4
    assert new_board[1][0] == -2
    assert delta == -6


def test_up_number_multiplier_merges() -> None:
    """Number and multiplier merge correctly when moving up."""
    board = [
        [-2, 0, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 2)
    assert new_board[0][0] == 4
    assert delta == 4


def test_up_number_and_multiplier_do_not_merge_without_tiles_above() -> None:
    """Number and multiplier stay separate when spaces exist above."""
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-2, 0, 0, 0],
        [2, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 2)
    assert new_board[0][0] == -2
    assert new_board[1][0] == 2
    assert delta == 0


def test_up_number_and_multiplier_no_merge_with_gap() -> None:
    """Number and multiplier remain apart when separated by a gap."""
    board = [
        [16, 0, 0, 0],
        [0, 0, 0, 0],
        [-2, 0, 0, 0],
        [2, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 2)
    assert new_board[0][0] == 16
    assert new_board[1][0] == -2
    assert new_board[2][0] == 2
    assert delta == 0
