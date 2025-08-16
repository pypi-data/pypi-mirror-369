"""Tests for downward moves and merges."""

import akioi_2048 as ak


def test_down_number_merges_and_positive_score() -> None:
    """Numbers merge when moving down and increase the score."""
    board = [
        [2, 0, 0, 0],
        [2, 0, 0, 0],
        [4, 0, 0, 0],
        [4, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 0)
    assert new_board[3][0] == 8
    assert new_board[2][0] == 4
    assert delta == 12


def test_down_multiplier_merges_and_negative_score() -> None:
    """Multipliers merge when moving down and decrease the score."""
    board = [
        [-1, 0, 0, 0],
        [-1, 0, 0, 0],
        [-2, 0, 0, 0],
        [-2, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 0)
    assert new_board[3][0] == -4
    assert new_board[2][0] == -2
    assert delta == -6


def test_down_number_multiplier_merges() -> None:
    """Number and multiplier merge correctly when moving down."""
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [2, 0, 0, 0],
        [-2, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 0)
    assert new_board[3][0] == 4
    assert delta == 4


def test_down_number_and_multiplier_do_not_merge_without_tiles_below() -> None:
    """Number and multiplier stay separate when spaces exist below."""
    board = [
        [2, 0, 0, 0],
        [-2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 0)
    assert new_board[2][0] == 2
    assert new_board[3][0] == -2
    assert delta == 0


def test_down_number_and_multiplier_no_merge_with_gap() -> None:
    """Number and multiplier remain apart when separated by a gap."""
    board = [
        [2, 0, 0, 0],
        [-2, 0, 0, 0],
        [0, 0, 0, 0],
        [16, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 0)
    assert new_board[1][0] == 2
    assert new_board[2][0] == -2
    assert new_board[3][0] == 16
    assert delta == 0


def test_down_move_without_merge() -> None:
    """Down move shifts tiles without merging."""
    board = [
        [-1, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 0)
    assert new_board[3][0] == -1
    assert new_board[3][1] == 2
    assert delta == 0


def test_no_merge_for_negative_four() -> None:
    """Negative four tiles do not merge when moving down."""
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-4, 0, 0, 0],
        [-4, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 0)
    assert new_board == board
    assert delta == 0
