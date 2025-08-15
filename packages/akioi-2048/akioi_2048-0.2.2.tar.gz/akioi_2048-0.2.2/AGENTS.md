# AGENTS

## Project Overview

- Rules are under rules directory.

## Development Workflow

- Format Rust code with `cargo fmt --all` before committing.
- Format Python code with `ruff format`.
- Run `maturin develop` followed by `pytest` to execute the full test suite.

## Notes

- Tests use the `uv` tool to manage Python dependencies.
