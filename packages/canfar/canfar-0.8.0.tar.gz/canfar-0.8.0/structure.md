# Project Structure

## Root Directory Layout
```
skaha/
├── skaha/              # Main package source code
├── tests/              # Test suite with comprehensive coverage
├── docs/               # MkDocs documentation source
├── .github/            # GitHub Actions CI/CD workflows
├── pyproject.toml      # Project configuration and dependencies
├── mkdocs.yml          # Documentation configuration
└── README.md           # Project overview and badges
```

## Main Package Structure (`skaha/`)
```
skaha/
├── __init__.py         # Package initialization, version, logging setup
├── client.py           # Core HTTP client with sync/async support
├── session.py          # Session management (extends client)
├── context.py          # Configuration context management
├── images.py           # Container image operations
├── overview.py         # Platform overview and status
├── auth/               # Authentication modules
│   ├── oidc.py         # OIDC token authentication
│   └── x509.py         # X.509 certificate authentication
├── cli/                # Command-line interface
│   ├── main.py         # CLI entry point and command registration
│   ├── auth.py         # Authentication commands
│   ├── config.py       # Configuration management commands
│   ├── create.py       # Session creation commands
│   ├── delete.py       # Resource deletion commands
│   ├── ps.py           # Process/session listing
│   └── [other_commands].py
├── models/             # Pydantic data models
│   ├── auth.py         # Authentication models
│   ├── config.py       # Configuration models
│   ├── session.py      # Session data models
│   ├── types.py        # Type definitions and enums
│   └── [other_models].py
├── exceptions/         # Custom exception classes
├── hooks/              # HTTP and CLI hooks/middleware
├── helpers/            # Utility functions for distributed computing
└── utils/              # General utilities (logging, JWT, etc.)
```

## Testing Structure (`tests/`)
- **Naming Convention**: `test_[module_name].py` mirrors source structure
- **Test Types**: Unit tests, integration tests, CLI tests
- **Fixtures**: Reusable test fixtures for clients, auth, mocking
- **Coverage**: HTML and XML reports generated in `htmlcov/` and `coverage.xml`

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

## Documentation Structure (`docs/`)
- **MkDocs**: Material theme with navigation structure
- **Content**: User guides, API reference, examples, changelog
- **Deployment**: Automated GitHub Pages deployment

## Configuration Files
- **pyproject.toml**: Single source of truth for all tool configuration
- **mkdocs.yml**: Documentation site configuration
- **.pre-commit-config.yaml**: Git hooks for code quality. The config for git hooks should still be in pyproject.toml.
- **uv.lock**: Dependency lock file for reproducible builds

## Key Architectural Patterns

### Functional Approach
- **Focus**: Simplicity, readability, and maintainability
- **Avoid**: Complex class hierarchies and code duplication
- **Keep it Simple**: Avoid over-engineering and unnecessary complexity
- **Clear Documentation**: Both user and developer focused documentation
- **Consistent Naming**: Clear, concise naming conventions for clarity
  - Example: `from skaha.utils import jwt -> jwt.expiry(token)`

### Client Composition
- `SkahaClient`: Base HTTP client with auth and configuration
- `Session`: Extends client for session-specific operations
- Both sync and async variants available
- **Auto-assembly**: Use automatic assembly behavior on instantiation (Pydantic best practices)

### CLI Organization
- Each command in separate module under `skaha/cli/`
- Typer-based with rich formatting and interactive prompts
- Command registration in `main.py`

### Model-Driven Design
- **Pydantic Models**: Use Pydantic for all data models and validation
- **Configuration**: Use pydantic_settings for configuration management
- Type safety and validation throughout
- Settings management with environment variable support

### Authentication Strategy
- Multiple auth contexts supported
- X.509 certificates, OIDC tokens and Bearer Tokens
- Configuration-driven auth selection

## Import Conventions
- Use absolute imports: `from skaha.models.auth import Token`
- Models imported from their specific modules
- Client classes imported directly: `from skaha.session import Session`
- CLI commands registered in main entry point

## Code Quality & Style Standards

### Type Safety Requirements
- **All functions must have complete type annotations**
- Include type hints for parameters, return values, and class attributes
- Use `from __future__ import annotations` for forward references
- Import types from `typing` module when needed: `Union`, `Dict`, etc.

### Documentation Standards
- **Google-style docstrings required** for all public APIs
- Include parameter types in docstrings even when type hints are present
- Provide comprehensive examples showing actual usage
- Add implementation notes, edge cases, and important warnings
- Use proper formatting with Args, Returns, Examples, Note sections

### File Structure Conventions
```python
"""Module docstring describing purpose."""

from __future__ import annotations

import standard_library_imports
from typing import TYPE_CHECKING, Any, Optional

import third_party_imports
from pydantic import BaseModel, Field

from skaha.models.auth import Token  # Absolute imports
from skaha.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

log = get_logger(__name__)
```

### String Encoding Best Practices
- Always specify encoding when opening files: `open(path, encoding="utf-8")`
- Use UTF-8 as default for all text operations
- Handle encoding errors gracefully in file operations
- Validate encoding when loading configuration files

### Development Workflow
- **Testing**: Always run `uv run pytest -m "not slow"` after each development step
- **Linting**: Run `uv run pre-commit run -a` before completing any task
- **Package Management**: Use `uv add` or `uv remove` - never manually edit dependencies

### Pre-commit Integration
- **MANDATORY**: Run `uv run pre-commit run -a` before completing any task
- Pre-commit hooks automatically enforce:
  - Ruff formatting and linting
  - MyPy type checking
  - Import sorting and organization
  - Security scanning with Bandit
  - Trailing whitespace and line ending fixes

### Git Commit Standards
- **Commitizen Style**: Use conventional commit format
- **Format**: `type(scope): description`
- **Types**: feat, fix, docs, style, refactor, test, chore
- **Examples**: 
  - `feat(auth): add OIDC token refresh`
  - `fix(session): handle timeout errors`
  - `docs(api): update session management examples`

### Example Module Structure
```python
"""Session management for CANFAR Science Platform.

This module provides both synchronous and asynchronous clients for managing
containerized sessions on the Science Platform.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional

from httpx import HTTPError, Response
from pydantic import Field, validator

from skaha import get_logger
from skaha.client import SkahaClient
from skaha.models.types import Kind, Status, View

if TYPE_CHECKING:
    from collections.abc import Iterator

log = get_logger(__name__)


class Session(SkahaClient):
    """Session management client for Science Platform.
    
    This class provides methods to manage containerized sessions including
    creation, monitoring, and cleanup operations.
    
    Args:
        timeout (int, optional): HTTP request timeout in seconds. Defaults to 30.
        concurrency (int, optional): Max concurrent connections. Defaults to 32.
        loglevel (str, optional): Logging level. Defaults to "INFO".
    
    Examples:
        >>> session = Session(timeout=60, loglevel="DEBUG")
        >>> sessions = session.fetch(kind="notebook", status="Running")
        >>> print(f"Found {len(sessions)} running notebooks")
        Found 3 running notebooks
    
    Note:
        Authentication is handled automatically based on configuration context.
        Both X.509 certificates and OIDC tokens are supported.
    """
    
    def fetch(
        self,
        kind: Optional[Kind] = None,
        status: Optional[Status] = None,
        view: Optional[View] = None,
    ) -> list[dict[str, str]]:
        """Fetch sessions matching the specified criteria.
        
        Args:
            kind (Optional[Kind]): Session type filter. Defaults to None.
            status (Optional[Status]): Session status filter. Defaults to None.
            view (Optional[View]): View level for response detail. Defaults to None.
        
        Returns:
            list[dict[str, str]]: List of session information dictionaries.
        
        Examples:
            >>> session = Session()
            >>> notebooks = session.fetch(kind="notebook", status="Running")
            >>> for nb in notebooks:
            ...     print(f"Session {nb['id']}: {nb['name']}")
            Session abc123: my-analysis
            Session def456: data-processing
        
        Raises:
            HTTPError: If the API request fails.
            AuthContextError: If authentication is invalid.
        """
```