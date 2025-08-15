#![deny(warnings)]
#![deny(clippy::all)]
#![deny(clippy::pedantic)]
#![deny(clippy::nursery)]
#![deny(clippy::cargo)]

use pyo3::prelude::*;
use pyo3::types::PyAny;

use rand::prelude::IndexedRandom;
use rand::{Rng, rng};

/// 4×4 board grid type
pub type Board = [[i32; 4]; 4];

const fn is_power_of_two(value: i32) -> bool {
    value > 0 && (value & (value - 1)) == 0
}

/// Internal move direction enum
#[derive(Clone, Copy)]
enum Action {
    Up,
    Down,
    Left,
    Right,
}

fn validate_board(board: &Board) -> PyResult<()> {
    for row in board {
        for &tile in row {
            let valid = tile == 0
                || ((2..=65_536).contains(&tile) && is_power_of_two(tile))
                || matches!(tile, -1 | -2 | -4);
            if !valid {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "invalid tile value: {tile}"
                )));
            }
        }
    }
    Ok(())
}

/// Lookup table for external direction indices.
///
/// * `0` → **Down**  ↓
/// * `1` → **Right** →
/// * `2` → **Up**    ↑
/// * `3` → **Left**  ←
const IDX_TO_ACTION: [Action; 4] = [Action::Down, Action::Right, Action::Up, Action::Left];

/// Apply one move; if the board changes a new tile is spawned at random.
///
/// :param list[list[int]] board:
///     4×4 board matrix.
///     * **Positive values** → Normal value tiles (2, 4, 8, …)
///     * **Negative values** → Multiplier tiles -1=×1, -2=×2, -4=×4; absolute value is the multiplier.
///
/// :param int dir:
///     Move direction:
///     * `0` = **Down**  ↓
///     * `1` = **Right** →
///     * `2` = **Up**    ↑
///     * `3` = **Left**  ←
///
/// :returns: *(`new_board`, `delta_score`, `msg`)*
///     * `new_board` `list[list[int]]` Board after the move
///     * `delta_score` `int` Score gained or lost from merges this move
///     * `msg` `int` Status flag
///         * `1`  → A `65536` tile was created → **Victory**
///         * `-1` → No possible moves in any direction → **Game Over**
///         * `0`  → Continue playing
///
/// :note:
///     If the move is invalid (board unchanged),
///     **no new tile is generated**, `delta_score = 0`, and `msg = 0`.
#[pyfunction]
fn step(py_board: &Bound<'_, PyAny>, direction: u8) -> PyResult<(Vec<Vec<i32>>, i32, i8)> {
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
fn init() -> Vec<Vec<i32>> {
    let mut rng = rng();
    let mut board: Board = [[0; 4]; 4];
    spawn_tile(&mut board, &mut rng);
    spawn_tile(&mut board, &mut rng);

    board.iter().map(|r| r.to_vec()).collect()
}

/// ---------- Pure logic ---------------------------------------------------------
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
    let victory = next.iter().flatten().any(|&v| v == 65_536);
    (next, delta, victory)
}

/// Rotate board 90°×k clockwise
fn rotate(board: Board, rotations: usize) -> Board {
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
fn slide_column(col: [i32; 4]) -> ([i32; 4], i32) {
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
    if a > 0 && b > 0 && a == b && a < 65_536 {
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
        v = v.min(65_536);
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
    let &(r, c) = empties.choose(rng).unwrap();

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

#[pymodule]
fn akioi_2048(_py: Python, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(step, module)?)?;
    module.add_function(wrap_pyfunction!(init, module)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "rotations must be 0..=3")]
    fn rotate_panics_on_invalid_k() {
        rotate([[0; 4]; 4], 4);
    }

    #[test]
    fn slide_column_merges_across_gap() {
        let (out, score) = slide_column([2, 0, 0, 2]);
        assert_eq!(out, [0, 0, 0, 4]);
        assert_eq!(score, 4);
    }

    #[test]
    fn slide_column_merges_multipliers() {
        let (out, score) = slide_column([-1, -1, -2, -2]);
        assert_eq!(out, [0, 0, -2, -4]);
        assert_eq!(score, -6);
    }

    #[test]
    fn slide_column_no_merge_for_negative_four() {
        let (out, score) = slide_column([0, 0, -4, -4]);
        assert_eq!(out, [0, 0, -4, -4]);
        assert_eq!(score, 0);
    }
}
