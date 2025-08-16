#[derive(Clone, Copy)]
pub enum Action {
    Up,
    Down,
    Left,
    Right,
}

/// Lookup table for external direction indices.
///
/// * `0` → **Down**  ↓
/// * `1` → **Right** →
/// * `2` → **Up**    ↑
/// * `3` → **Left**  ←
pub const IDX_TO_ACTION: [Action; 4] = [Action::Down, Action::Right, Action::Up, Action::Left];
