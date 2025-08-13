# Repository Guidelines

## Project Structure & Modules
- Source: `skaha/` (CLI in `skaha/cli`, models in `skaha/models`, helpers/hooks under `skaha/helpers` and `skaha/hooks`).
- Tests: `tests/` (unit and integration; files named `test_*.py`).
- Docs: `docs/` with MkDocs config in `mkdocs.yml`.
- Packaging: `pyproject.toml` (Hatchling); entry points: `skaha`, `canfar`, `cf`.

## Build, Test, and Dev Commands
- Environment: `uv python install 3.13 && uv venv --python 3.13 && uv sync --dev`
- Run CLI locally: `uv run skaha --help` (aliases: `canfar`, `cf`).
- Tests (all): `uv run pytest` (skip slow: `-m "not slow"`).
- Coverage reports: generated via pytest; threshold set to 80% (XML/HTML output).
- Lint/format: `uv run ruff check --fix .` and `uv run ruff format .`.
- Type-check: `uv run mypy skaha`.
- Pre-commit: `uv run pre-commit run -a` (install hooks: `uv run pre-commit install --hook-type commit-msg`).
- Build distribution: `uv build`.

## Coding Style & Naming
- Python 3.10+; indent 4 spaces; max line length 88.
- Imports, lint, and formatting via Ruff (isort, pycodestyle, bugbear, etc.).
- Docstrings use Google style; prefer full type hints (MyPy strict settings enabled).
- Naming: modules/functions/vars `snake_case`; classes `PascalCase`; constants `UPPER_SNAKE_CASE`.

## Testing Guidelines
- Framework: pytest with `pytest-asyncio`, `xdist` (parallel), and markers (`unit`, `integration`, `slow`).
- Place tests under `tests/` and name `test_*.py`; mark slow/integration appropriately.
- Run fast suite during dev: `uv run pytest -m "not slow"`; run full suite before PR.

## Commit & Pull Requests
- Commits: follow Conventional Commits (e.g., `feat: add session retry`).
- PRs: include summary, linked issues, test coverage (≥80%), and any docs updates.
- CI expectations: lint, type-check, tests, and security hooks (detect-secrets/gitleaks) must pass.

## Security & Configuration
- Secrets: never commit credentials; pre-commit runs secret scanners.
- Optional checks: `uv run bandit -r skaha -c pyproject.toml` and `uv run vulture skaha tests`.
