import akioi_2048 as ak


def test_step_smoke():
    board = ak.init()
    new_board, delta, msg = ak.step(board, 0)
    assert len(new_board) == 4 and all(len(r) == 4 for r in new_board)
    assert isinstance(delta, int)
    assert msg in (-1, 0, 1)
