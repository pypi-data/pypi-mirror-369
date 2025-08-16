use pyo3::prelude::*;

mod actions;
mod board;
mod game;

pub use crate::game::{init, step};

#[pymodule]
fn akioi_2048(_py: Python, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(step, module)?)?;
    module.add_function(wrap_pyfunction!(init, module)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use crate::game::{rotate, slide_column};

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
