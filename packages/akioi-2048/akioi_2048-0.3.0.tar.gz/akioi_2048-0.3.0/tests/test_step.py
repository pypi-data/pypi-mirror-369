import akioi_2048 as ak
import pytest


def test_step_smoke():
    board = ak.init()
    new_board, delta, msg = ak.step(board, 0)
    assert len(new_board) == 4 and all(len(r) == 4 for r in new_board)
    assert isinstance(delta, int)
    assert msg in (-1, 0, 1)


def test_number_merges_and_positive_score():
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


def test_multiplier_merges_and_negative_score():
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


def test_no_merge_for_negative_four():
    board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-4, 0, 0, 0],
        [-4, 0, 0, 0],
    ]
    new_board, delta, _ = ak.step(board, 0)
    assert new_board == board
    assert delta == 0


def test_down_move_without_merge():
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


def test_number_and_multiplier_do_not_merge_without_tiles_below():
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


def test_number_and_multiplier_no_merge_with_gap():
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


def test_step_rejects_non_power_of_two():
    board = [
        [3, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    with pytest.raises(ValueError):
        ak.step(board, 0)


def test_step_rejects_too_large_value():
    board = [
        [131072, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    with pytest.raises(ValueError):
        ak.step(board, 0)


def test_step_rejects_unknown_negative_multiplier():
    board = [
        [-3, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    with pytest.raises(ValueError):
        ak.step(board, 0)


def test_step_rejects_one():
    board = [
        [1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    with pytest.raises(ValueError):
        ak.step(board, 0)
