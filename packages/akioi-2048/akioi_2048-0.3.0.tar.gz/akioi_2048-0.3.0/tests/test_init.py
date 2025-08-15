import akioi_2048 as ak

ALLOWED = {-2, -1, 2, 4}


def flatten(board):
    return [c for row in board for c in row]


def test_init_board():
    board = ak.init()
    flat = flatten(board)
    non_zero = [x for x in flat if x]
    assert len(flat) == 16
    assert len(non_zero) == 2
    assert all(x in ALLOWED for x in non_zero)
