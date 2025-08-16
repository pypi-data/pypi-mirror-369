"""Tests for invalid tile inputs."""

import pytest

import akioi_2048 as ak


def test_step_rejects_non_power_of_two() -> None:
    """Reject tiles that are not powers of two."""
    board = [
        [3, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    with pytest.raises(ValueError, match=r"^invalid tile value: 3$"):
        ak.step(board, 0)


def test_step_rejects_too_large_value() -> None:
    """Reject tiles larger than the maximum allowed."""
    board = [
        [131072, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    with pytest.raises(ValueError, match=r"^invalid tile value: 131072$"):
        ak.step(board, 0)


def test_step_rejects_unknown_negative_multiplier() -> None:
    """Reject negative multipliers other than -1, -2, or -4."""
    board = [
        [-3, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    with pytest.raises(ValueError, match=r"^invalid tile value: -3$"):
        ak.step(board, 0)


def test_step_rejects_one() -> None:
    """Reject the value one, which is not allowed."""
    board = [
        [1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    with pytest.raises(ValueError, match=r"^invalid tile value: 1$"):
        ak.step(board, 0)
