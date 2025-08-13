# Technology Stack

## Build System
- **Build Backend**: Hatchling (modern Python packaging)
- **Package Manager**: uv (fast Python package installer and resolver)
- **Python Version**: 3.10+ (supports 3.10, 3.11, 3.12, 3.13)

## Core Dependencies
- **HTTP Client**: httpx with HTTP/2 support for async/sync API calls
- **CLI Framework**: Typer for command-line interface with rich formatting
- **Data Validation**: Pydantic v2 with settings management
- **Configuration**: YAML/TOML support with pydantic-settings
- **Authentication**: cadcutils for CANFAR-specific auth, cryptography for X.509
- **UI/UX**: Rich for terminal formatting, questionary for interactive prompts
- **QR Codes**: segno for authentication QR code generation

## Development Tools
- **Linting & Formatting**: Ruff (replaces black, isort, flake8, pylint)
- **Type Checking**: MyPy with strict configuration
- **Testing**: pytest with asyncio, coverage, mock, and parallel execution
- **Security**: Bandit for security linting
- **Pre-commit**: Automated code quality checks
- **Documentation**: MkDocs with Material theme

## Common Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Install with development dependencies
uv sync --dev

# Install with docs
uv sync --group docs

# Activate virtual environment
source .venv/bin/activate
```

### Testing
```bash
# MANDATORY: Run after each development step
uv run pytest -m "not slow"

# Run all tests with coverage
uv run pytest

# Run tests in parallel
uv run pytest -n auto

# Run specific test types
uv run pytest -m "not integration"  # Skip integration tests
uv run pytest -m unit              # Run only unit tests
uv run pytest -m slow              # Run only slow tests
```

## Testing Framework & Organization
- **Framework**: pytest with asyncio, coverage, mock, and parallel execution
- **Location**: All tests under `tests/` directory
- **Naming**: Follow pattern `test_[module_name].py` mirrors source structure
- **Approach**: Functional approach over class-based for readability
- **Test Execution**: `uv run pytest` for all tests, `uv run pytest -m "not slow"` for fast tests only
- **Speed**: Make tests fast and async when possible
- **Sequential Tests**: Use `mark.order` for tests that must run sequentially
- **Slow Tests**: Mark with 'slow' marker for long-running tests

## Test Strategy
- **Coverage**: Aim for 80% coverage with comprehensive tests
- **Quality**: Write concise and readable tests that can run in isolation
- **Scope**: Test multiple code paths including error handling and edge cases
- **Integration**: Include large-scale integration tests alongside unit tests
- **Verification**: Always run tests after writing to verify they pass
- **Auth Mode**: Tests run with the `default` auth mode using X509 hardcoded values

### Code Quality
```bash
# Format and lint code
uv run ruff format .
uv run ruff check .

# Type checking
uv run mypy skaha/

# Run pre-commit hooks
pre-commit run --all-files
```

### Documentation
```bash
# Serve docs locally
mkdocs serve

# Build documentation
mkdocs build

# You can browse the documentation locally by running `mkdocs serve` and navigating to `http://localhost:8000` in your web browser.
```

## Documentation Framework & Tools
- **Documentation System**: Material for MkDocs theme
- **Deployment**: Built and deployed using mike
- **Location**: All docs in `docs/` folder
- **Build Command**: `mkdocs build`
- **Serve Command**: `mkdocs serve`
- **Local Access**: Browse documentation at `http://localhost:8000` after running `mkdocs serve`

## Documentation Content Standards
- **Rich Features**: Use admonitions, annotations, buttons, code blocks, icons, emojis, tooltips
- **Authentication Docs**: Create detailed markdown docs for authentication processes

### CLI Usage
```bash
# Install in development mode
pip install -e .

# Run CLI
skaha --help
skaha auth login
skaha ps
```

## Package Management Standards
- **Primary Tool**: Use uv for all dependency and virtual environment management
- **Configuration**: Define all tool configurations in pyproject.toml
- **No Manual Editing**: Never manually edit package dependencies - always use package manager
- **Adding Dependencies**: `uv add package-name`
- **Removing Dependencies**: `uv remove package-name`
- **Development Dependencies**: `uv add --dev package-name`

## Configuration Standards
- Use pyproject.toml for all tool configuration
- Ruff handles formatting, linting, and import sorting
- MyPy strict mode with Pydantic plugin
- pytest with asyncio mode and parallel execution
- Coverage minimum threshold: 80%

## Git Commit Standards
- **Commitizen Style**: Use conventional commit format for all git commits
- **Format**: `type(scope): description`
- **Types**: feat, fix, docs, style, refactor, test, chore
- **Examples**: 
  - `feat(auth): add OIDC token refresh`
  - `fix(session): handle timeout errors`
  - `docs(api): update session management examples`
  - `test(client): add authentication test cases`

## Code Quality & Style Requirements

### Type Annotations
- **Always** include type hints for all function parameters, return values, and variables
- Use proper type annotations from `typing` module when needed
- Follow PEP 484 and modern typing practices

### Documentation Standards
- **Google-style docstrings** for all public functions, classes, and methods
- Include type information in docstring parameters (even with type hints)
- Provide comprehensive examples in docstrings when possible
- Add implementation notes and edge case documentation
- Use proper markdown formatting in docstrings

### String Encoding
- Always specify encoding when reading/writing files: `open(file, encoding="utf-8")`
- Handle encoding properly when loading configuration or data files
- Use UTF-8 as default encoding for all text operations

### Pre-commit Workflow
```bash
# ALWAYS run before finishing any task
uv run pre-commit run -a

# This will automatically:
# - Format code with Ruff
# - Check linting rules
# - Validate type hints with MyPy
# - Run security checks with Bandit
# - Fix import sorting and other style issues
```

### Example Code Style
```python
def create_session(
    name: str,
    image: str,
    cores: int = 2,
    ram: int = 4,
) -> list[str]:
    """Create a new containerized session.
    
    Args:
        name (str): Unique session name for identification.
        image (str): Container image URI to use for the session.
        cores (int, optional): Number of CPU cores to allocate. Defaults to 2.
        ram (int, optional): RAM allocation in GB. Defaults to 4.
    
    Returns:
        list[str]: List of session IDs for created sessions.
    
    Examples:
        >>> session = Session()
        >>> ids = session.create_session(
        ...     name="analysis-job",
        ...     image="images.canfar.net/skaha/notebook:latest",
        ...     cores=4,
        ...     ram=8
        ... )
        >>> print(f"Created sessions: {ids}")
        Created sessions: ['abc123', 'def456']
    
    Note:
        Session names must be unique within the user's namespace.
        Resource allocation is subject to platform limits.
    """
```