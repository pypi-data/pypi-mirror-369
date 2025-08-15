# akioi-2048


A Python implementation of a customizable 2048 game engine with support for multiplier tiles and score tracking.

## Features

- Classic 2048 mechanics
- Special multiplier tiles: -1 (×1), -2 (×2), -4 (×4)
- Supports programmatic interaction for AI training
- Detects victory (65536 tile) and game over states

## Python Public Functions

### `step(board, direction)`

Executes one move in the given direction and, if the move changes the board, generates a new tile.

#### Parameters

- **`board: list[list[int]]`**  
  4×4 board matrix.  
  - Positive integers represent normal value tiles (2, 4, 8, …).  
  - Negative integers represent multiplier tiles:  
    - `-1` = ×1  
    - `-2` = ×2  
    - `-4` = ×4  
    The absolute value of the number is the multiplier.

- **`direction: int`**  
  Direction of movement:  
  - `0` → **Down** ↓  
  - `1` → **Right** →  
  - `2` → **Up** ↑  
  - `3` → **Left** ←  

#### Returns

A tuple **`(new_board, delta_score, msg)`**:

- **`new_board: list[list[int]]`** — Board after the move  
- **`delta_score: int`** — Score gained from merges during this move  
- **`msg: int`** — Game state indicator:
  - `1` → A tile with value 65536 was created → **Victory**
  - `-1` → No legal moves left → **Game Over**
  - `0` → Game continues

#### Notes

If the move is invalid (board remains unchanged), no new tile is generated, `delta_score = 0`, and `msg = 0`.

### `init()`
Init a new board
#### Returns
A table **`new_board`**  
- **`new_board: list[list[int]]` A new board

## Installation

Install via `pip`:

```bash
pip3 install akioi-2048
````
