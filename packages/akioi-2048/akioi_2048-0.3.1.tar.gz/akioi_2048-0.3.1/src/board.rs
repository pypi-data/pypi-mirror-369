use pyo3::prelude::*;

/// 4×4 board grid type
pub type Board = [[i32; 4]; 4];

/// Ensure all tiles on the board are valid
pub fn validate_board(board: &Board) -> PyResult<()> {
    for row in board {
        for &tile in row {
            let valid = tile == 0
                || ((2..=0x0001_0000).contains(&tile)
                    && u32::try_from(tile).is_ok_and(u32::is_power_of_two))
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
