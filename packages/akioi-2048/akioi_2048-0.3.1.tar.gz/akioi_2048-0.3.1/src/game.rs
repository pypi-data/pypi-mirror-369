use pyo3::prelude::*;
use pyo3::types::PyAny;
use rand::prelude::IndexedRandom;
use rand::{Rng, rng};

use crate::actions::{Action, IDX_TO_ACTION};
use crate::board::{Board, validate_board};

/// Apply one move; if the board changes a new tile is spawned at random.
///
/// # Errors
/// Returns a [`PyErr`] if the board contains invalid tiles or `direction` is not in `0..=3`.
#[pyfunction]
pub fn step(py_board: &Bound<'_, PyAny>, direction: u8) -> PyResult<(Vec<Vec<i32>>, i32, i8)> {
    // ① Convert Python list into a Rust board
    let board: Board = py_board.extract()?;

    validate_board(&board)?;

    // ② Map `direction` to `Action`
    let action = IDX_TO_ACTION
        .get(direction as usize)
        .copied()
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("direction must be 0-3"))?;

    let mut rng = rng();

    // ③ Perform one logical step
    let (mut next, delta, victory) = single_step(&board, action);

    let moved = next != board;
    if moved {
        spawn_tile(&mut next, &mut rng); // rule: spawn a tile after a valid move
    }

    // ④ Check failure (no moves in any direction)
    let dead = (0..4).all(|d| single_step(&next, IDX_TO_ACTION[d]).0 == next);

    let msg = if victory {
        1
    } else if dead {
        -1
    } else {
        0
    };

    Ok((next.iter().map(|r| r.to_vec()).collect(), delta, msg))
}

/// Initialize a new board with two tiles
///
/// :returns: `new_board`
///     * `new_board` `list[list[int]]` A fresh board
#[pyfunction]
#[must_use]
pub fn init() -> Vec<Vec<i32>> {
    let mut rng = rng();
    let mut board: Board = [[0; 4]; 4];
    spawn_tile(&mut board, &mut rng);
    spawn_tile(&mut board, &mut rng);

    board.iter().map(|r| r.to_vec()).collect()
}

/// Return `(new_board, delta_score, victory?)` (no random tile spawn)
fn single_step(board: &Board, action: Action) -> (Board, i32, bool) {
    let rot = match action {
        Action::Down => 0,  // ↓
        Action::Up => 2,    // ↑ rotate 180°
        Action::Left => 3,  // ← rotate -90°
        Action::Right => 1, // → rotate +90°
    };
    let mut work = rotate(*board, rot);

    let mut delta = 0;
    for c in 0..4 {
        let (col, add) = slide_column([work[0][c], work[1][c], work[2][c], work[3][c]]);
        delta += add;
        for r in 0..4 {
            work[r][c] = col[r];
        }
    }
    let next = rotate(work, (4 - rot) % 4);
    let victory = next.iter().flatten().any(|&v| v == 0x0001_0000);
    (next, delta, victory)
}

/// Rotate board 90°×k clockwise
pub fn rotate(board: Board, rotations: usize) -> Board {
    assert!(rotations < 4, "rotations must be 0..=3");
    let mut rotated = [[0; 4]; 4];
    for (src_row_idx, row) in board.iter().enumerate() {
        for (src_col_idx, &val) in row.iter().enumerate() {
            let (dest_row_idx, dest_col_idx) = match rotations {
                0 => (src_row_idx, src_col_idx),
                1 => (src_col_idx, 3 - src_row_idx),
                2 => (3 - src_row_idx, 3 - src_col_idx),
                3 => (3 - src_col_idx, src_row_idx),
                _ => unreachable!("rotations must be 0..=3"),
            };
            rotated[dest_row_idx][dest_col_idx] = val;
        }
    }
    rotated
}

/// Process one column: scan upward, merge, and drop tiles.
/// Return `(new_column, score_delta)`
///
/// * Scan pointer `r` from 3 down to 0.
/// * Write pointer `w` from 3 down to 0 (always filling bottom up).
pub fn slide_column(col: [i32; 4]) -> ([i32; 4], i32) {
    let mut out = [0i32; 4];
    let mut score = 0;
    let mut w: usize = 3; // write position (bottom to top)
    let mut r = Some(3usize); // read pointer (bottom to top)

    while let Some(i) = r {
        // skip empty cells
        if col[i] == 0 {
            r = i.checked_sub(1);
            continue;
        }

        // find first non-zero above
        let mut s = i.checked_sub(1);
        while let Some(j) = s {
            if col[j] != 0 {
                break;
            }
            s = j.checked_sub(1);
        }

        // try merging i and s
        if let Some(j) = s {
            let below_slice = &col[(i + 1)..4]; // slice is empty if i=3
            if let Some((tile, add)) = try_merge(col[i], col[j], i == j + 1, below_slice) {
                out[w] = tile;
                score += add;
                w = w.saturating_sub(1);
                r = j.checked_sub(1); // skip the merged tile
                continue;
            }
        }

        out[w] = col[i];
        w = w.saturating_sub(1);
        r = i.checked_sub(1);
    }

    (out, score)
}

/// Determine and perform a merge
fn try_merge(a: i32, b: i32, adjacent: bool, below: &[i32]) -> Option<(i32, i32)> {
    // numeric + numeric
    if a > 0 && b > 0 && a == b && a < 0x0001_0000 {
        return Some((a + b, a + b));
    }
    // multiplier + multiplier
    if a < 0 && b < 0 && a == b && a > -4 {
        return Some((a * 2, a * 2));
    }
    // numeric + multiplier
    if a * b < 0 && adjacent && (below.is_empty() || below.iter().all(|&v| v != 0)) {
        let num = if a > 0 { a } else { b };
        let mul = if a < 0 { a } else { b };
        let mut v = num * mul.abs();
        v = v.min(0x0001_0000);
        return Some((v, v));
    }
    None
}

/// Spawn a random tile on an empty cell (same probabilities as the web version)
fn spawn_tile<R: Rng>(board: &mut Board, rng: &mut R) {
    // ① Gather empty coordinates (avoid closure to skip move)
    let mut empties = Vec::new();
    for (r, row) in board.iter().enumerate() {
        for (c, &val) in row.iter().enumerate() {
            if val == 0 {
                empties.push((r, c));
            }
        }
    }
    if empties.is_empty() {
        return;
    }

    // ② Pick a random position
    let Some(&(r, c)) = empties.choose(rng) else {
        return;
    };

    // ③ Generate a tile using weighted probabilities
    // TODO: The probabilities below do not match the documentation in
    // `rules/source.php`. Update once the documentation is corrected.
    let p: f64 = rng.random();
    board[r][c] = if p < 0.783 {
        2
    } else if p < 0.861 {
        4
    } else if p < 0.9728 {
        -1 // ×1
    } else {
        -2 // ×2
    };
}
