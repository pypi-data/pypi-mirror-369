# AGENTS

## Project Overview

- Game rules reside under the `rules/` directory.

## Workflow

### Staging

- Always stage changes using `git add .`.

### Formatting

Run the following commands before committing:

```bash
cargo fmt --all
uv tool run ruff format
npx prettier --write "**/*.{md,yml,yaml,js,ts,json}"
taplo format "**/*.toml"
```

### Checks

Execute these checks to validate your changes:

```bash
cargo clippy --all-targets --all-features -- -D warnings
uv tool run ruff check .
mado check .
uv venv .venv
source .venv/bin/activate
uv run maturin develop
uv run pytest
```
