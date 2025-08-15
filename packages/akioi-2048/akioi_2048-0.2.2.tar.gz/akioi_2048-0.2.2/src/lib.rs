use pyo3::prelude::*;
use pyo3::types::PyAny;

use rand::prelude::IndexedRandom;
use rand::{Rng, rng};

/// 4×4 棋盘类型
pub type Board = [[i32; 4]; 4];

/// 内部方向枚举
#[derive(Clone, Copy)]
enum Action {
    Up,
    Down,
    Left,
    Right,
}

/// Execute a move and (if successful) randomly generate a new tile.
///
/// :param list[list[int]] board:
///     4×4 board matrix.  
///     * **Positive values** → Normal value tiles (2, 4, 8, …)  
///     * **Negative values** → Multiplier tiles  -1=×1, -2=×2, -4=×4; absolute value is the multiplier.  
///
/// :param int dir:
///     Move direction:  
///     * `0` = **Down**  ↓  
///     * `1` = **Right** →  
///     * `2` = **Up**    ↑  
///     * `3` = **Left**  ←  
///
/// :returns: *(new_board, delta_score, msg)*  
///     * **new_board** `list[list[int]]` Board after the move  
///     * **delta_score** `int` Score gained/lost from merges this move  
///     * **msg** `int` Status flag  
///         * `1`  → A `65536` tile was created  → **Victory**  
///         * `-1` → No possible moves in any direction → **Game Over**  
///         * `0`  → Continue playing
///
/// :note:
///     If the move is invalid (board unchanged),  
///     **no new tile is generated**, `delta_score = 0`, and `msg = 0`.
#[pyfunction]
fn step(py_board: &Bound<'_, PyAny>, direction: u8) -> PyResult<(Vec<Vec<i32>>, i32, i8)> {
    // ① Python → Rust Board
    let raw: Vec<Vec<i32>> = py_board.extract()?;
    if raw.len() != 4 || raw.iter().any(|r| r.len() != 4) {
        return Err(pyo3::exceptions::PyValueError::new_err("board must be 4×4"));
    }
    let mut board: Board = [[0; 4]; 4];
    for (r, row) in raw.iter().enumerate() {
        for (c, &v) in row.iter().enumerate() {
            board[r][c] = v;
        }
    }

    // ② direction → Action
    let action = match direction {
        0 => Action::Down,
        1 => Action::Right,
        2 => Action::Up,
        3 => Action::Left,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "direction must be 0-3",
            ));
        }
    };

    let mut rng = rng();

    // ③ 执行一步
    let (mut next, delta, victory) = single_step(&board, action);

    let moved = next != board;
    if moved {
        spawn_tile(&mut next, &mut rng); // 规则：有效移动后随机生成一块
    }

    // ④ 判断失败（四方向都无法动）
    let dead = !moved && (0..4).all(|d| single_step(&next, idx_to_action(d)).0 == next);

    let msg = if victory {
        1
    } else if dead {
        -1
    } else {
        0
    };

    Ok((next.iter().map(|r| r.to_vec()).collect(), delta, msg))
}

/// Init a new board
///
/// :returns: *new_board*  
///     * **new_board** `list[list[int]]` A new board
#[pyfunction]
fn init() -> PyResult<Vec<Vec<i32>>> {
    let mut rng = rng();
    let mut board: Board = [[0; 4]; 4];
    spawn_tile(&mut board, &mut rng);
    spawn_tile(&mut board, &mut rng);

    Ok(board.iter().map(|r| r.to_vec()).collect())
}

/// ---------- 纯逻辑 ---------------------------------------------------------

/// 返回 `(new_board, delta_score, victory?)`（不生成随机砖）
fn single_step(board: &Board, action: Action) -> (Board, i32, bool) {
    let rot = match action {
        Action::Down => 0,  // ↓
        Action::Up => 2,    // ↑ 旋转 180°
        Action::Left => 3,  // ← 旋转 -90°
        Action::Right => 1, // → 旋转 +90°
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

fn idx_to_action(i: usize) -> Action {
    [Action::Up, Action::Down, Action::Left, Action::Right][i]
}

/// 旋转棋盘 90°×k（顺时针）
fn rotate(b: Board, k: usize) -> Board {
    let mut r = [[0; 4]; 4];
    match k % 4 {
        0 => b,
        1 => {
            for i in 0..4 {
                for j in 0..4 {
                    r[j][3 - i] = b[i][j];
                }
            }
            r
        }
        2 => {
            for i in 0..4 {
                for j in 0..4 {
                    r[3 - i][3 - j] = b[i][j];
                }
            }
            r
        }
        3 => {
            for i in 0..4 {
                for j in 0..4 {
                    r[3 - j][i] = b[i][j];
                }
            }
            r
        }
        _ => r,
    }
}

/// 处理一列：自底向上扫描、合并、下落。
/// 返回 `(新列, 得分增量)`
///
/// * 扫描指针 `r` 从 3 ↓ 0。  
/// * 输出指针 `w` 从 3 ↓ 0（始终保持列底向上写入）。  
fn slide_column(col: [i32; 4]) -> ([i32; 4], i32) {
    let mut out = [0i32; 4];
    let mut w: i32 = 3; // 写入位置（从底往上）
    let mut score = 0;
    let mut r: i32 = 3; // 读指针（从底往上）

    while r >= 0 {
        // 跳过空格
        if col[r as usize] == 0 {
            r -= 1;
            continue;
        }

        // 寻找上方第一个非零
        let mut s = r - 1;
        while s >= 0 && col[s as usize] == 0 {
            s -= 1;
        }

        // 尝试合并 r 与 s
        let merged = if s >= 0 {
            let below_slice = &col[(r as usize + 1)..4]; // r=3 时 slice 为空
            try_merge(col[r as usize], col[s as usize], r == s + 1, below_slice)
        } else {
            None
        };

        match merged {
            Some((tile, add)) => {
                out[w as usize] = tile;
                score += add;
                w -= 1;
                r = s - 1; // 跳过被合并的那块
            }
            None => {
                out[w as usize] = col[r as usize];
                w -= 1;
                r -= 1;
            }
        }
    }

    (out, score)
}

/// 判定并执行合并
fn try_merge(a: i32, b: i32, adjacent: bool, below: &[i32]) -> Option<(i32, i32)> {
    // 数值 + 数值
    if a > 0 && b > 0 && a == b && a < 65_536 {
        return Some((a + b, a + b));
    }
    // 倍增 + 倍增
    if a < 0 && b < 0 && a == b && a > -4 {
        return Some((a * 2, a * 2));
    }
    // 数值 + 倍增
    if a * b < 0 && adjacent && (below.is_empty() || below.iter().all(|&v| v != 0)) {
        let num = if a > 0 { a } else { b };
        let mul = if a < 0 { a } else { b };
        let v = num * mul.abs();
        return Some((v, v));
    }
    None
}

/// 随机在空格生成一块新砖（权重同网页规则）
fn spawn_tile<R: Rng>(board: &mut Board, rng: &mut R) {
    // ① 收集空格坐标（不再用闭包，避免 move）
    let mut empties = Vec::new();
    for r in 0..4 {
        for c in 0..4 {
            if board[r][c] == 0 {
                empties.push((r, c));
            }
        }
    }
    if empties.is_empty() {
        return;
    }

    // ② 随机挑选位置
    let &(r, c) = empties.choose(rng).unwrap();

    // ③ 按权重生成方块
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
fn akioi_2048(_py: Python, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(step, &m)?)?;
    m.add_function(wrap_pyfunction!(init, &m)?)?;
    Ok(())
}
