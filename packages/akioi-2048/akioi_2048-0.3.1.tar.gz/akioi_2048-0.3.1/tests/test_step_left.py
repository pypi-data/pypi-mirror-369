"""Tests for leftward moves and merges."""

import akioi_2048 as ak


def test_left_number_merges_and_positive_score() -> None:
    """Numbers merge when moving left and increase the score."""
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [4, 4, 2, 2],
    ]
    new_board, delta, _ = ak.step(board, 3)
    assert new_board[3][0] == 8
    assert new_board[3][1] == 4
    assert delta == 12


def test_left_multiplier_merges_and_negative_score() -> None:
    """Multipliers merge when moving left and decrease the score."""
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-2, -2, -1, -1],
    ]
    new_board, delta, _ = ak.step(board, 3)
    assert new_board[3][0] == -4
    assert new_board[3][1] == -2
    assert delta == -6


def test_left_number_multiplier_merges() -> None:
    """Number and multiplier merge correctly when moving left."""
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-2, 2, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 3)
    assert new_board[3][0] == 4
    assert delta == 4


def test_left_number_and_multiplier_do_not_merge_without_tiles_left() -> None:
    """Number and multiplier stay separate when spaces exist to the left."""
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, -2, 2, 0],
    ]
    new_board, delta, _ = ak.step(board, 3)
    assert new_board[3][0] == -2
    assert new_board[3][1] == 2
    assert delta == 0


def test_left_number_and_multiplier_no_merge_with_gap() -> None:
    """Number and multiplier remain apart when separated by a gap."""
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [16, 0, -2, 2],
    ]
    new_board, delta, _ = ak.step(board, 3)
    assert new_board[3][0] == 16
    assert new_board[3][1] == -2
    assert new_board[3][2] == 2
    assert delta == 0
