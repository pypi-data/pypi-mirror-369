# Product Overview

Skaha is a Python client library for the CANFAR Science Platform, designed to provide programmatic access to container-based scientific computing resources.

## Core Purpose
- **Container Management**: Create, manage, and monitor containerized sessions for scientific computing
- **Authentication**: Support for both X.509 certificates, Bearer Tokens and OIDC token-based authentication
- **CLI Interface**: Full-featured command-line interface for platform interaction
- **Async Support**: Both synchronous and asynchronous client implementations

## Configuration Structure
- Server information where the client connects to is defined in `skaha.models.http.Server`
- Authentication methods to support: `oidc`, `x509` and `default`.
- `default` is `x509` with hardcoded values.
- The user can provide runtime `token` or `certificate` fields to override the default authentication method. The `token` can be anything: PAT, Bearer, Custom, etc. The `certificate` is a path to a PEM file.
- Users login via `skaha auth login` which guides the user through the authentication process and saves the credentials to the Configuration model, which is then saved to disk and at later time used to configure the httpx client.

## Auth HTTP Hooks
- Check if auth is expired before requests are sent only if the auth mode is `oidc`
- OIDC Refresh is handled automatically by httpx hooks
- All other auth types are not refreshed automatically, instead a `401` response is returned to the user to re-authenticate.
- Bypass refresh for user-passed tokens/certs

## Key Features
- Session lifecycle management (create, monitor, destroy)
- Container image management and discovery
- Resource allocation (CPU, RAM, GPU)
- Event logging and monitoring
- Configuration management with multiple authentication contexts
- Rich CLI with interactive prompts and formatted output

## Target Users
- Astronomers and researchers using CANFAR infrastructure
- System administrators managing scientific computing resources
- Developers building applications on top of the Science Platform

## Architecture
- Client-server model with HTTP/REST API communication
- Pydantic-based configuration and data validation
- Modular design with separate concerns for auth, sessions, images, etc.
- Support for both headless and interactive session types

## Architecture Patterns
- **Functional Approach**: Focus on simplicity, readability, and maintainability
- **Avoid Complexity**: No complex class hierarchies or code duplication
- **Keep it Simple**: Avoid over-engineering and unnecessary complexity
- **Clear Documentation**: Both user and developer focused documentation
- **Consistent Naming**: Clear, concise naming conventions which feel intuitive when reading code (e.g., `from skaha.utils import funny -> name = funny.name()`)
- **Auto-assembly**: Use automatic assembly behavior on instantiation (Pydantic best practices)
- **Pydantic Models**: Use Pydantic for data models and validation
- **Configuration**: Use pydantic_settings for configuration management

## Code Quality Standards
- **Type Safety**: All Python code must include proper type hints and annotations
- **Documentation**: Google-style docstrings with comprehensive examples and implementation notes
- **String Handling**: Proper encoding when loading data from files
- **Quality Gates**: Pre-commit hooks enforce linting, formatting, and style consistency
- **Testing**: Run `uv run pytest -m "not slow"` after each development step
- **Linting**: Run `uv run pre-commit run -a` before completing tasks

## Package Management
- **Primary Tool**: Use uv for all dependency and virtual environment management
- **Configuration**: Define all tool configurations in pyproject.toml
- **No Manual Editing**: Never manually edit package dependencies - always use `uv add` or `uv remove`

## Git Commit Standards
- **Commitizen Style**: Use conventional commit format for all git commits
- Format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Examples: `feat(auth): add OIDC token refresh`, `fix(session): handle timeout errors`