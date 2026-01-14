# AGENTS.md

This file provides guidance for AI coding agents working on the **sphinx-pytest** repository.

## Project Overview

sphinx-pytest provides helpful pytest fixtures for testing Sphinx extensions. It simplifies the process of creating Sphinx test applications and accessing built doctrees.

## Repository Structure

```
pyproject.toml          # Project configuration and dependencies
tox.ini                 # Tox test environment configuration

src/sphinx_pytest/      # Main source code
├── __init__.py         # Package init with version
├── builders.py         # Custom Sphinx builders for testing
└── plugin.py           # Pytest plugin with fixtures

tests/                  # Test suite
└── test_basic.py       # Basic tests
```

## Development Commands

### Testing

```bash
# Run all tests
tox

# Run with a specific Python version
tox -e py312

# Run specific tests
tox -- tests/test_basic.py -v
```

### Code Quality

```bash
# Type checking with mypy
tox -e mypy

# Linting with ruff (auto-fix enabled)
tox -e ruff-check

# Formatting with ruff
tox -e ruff-fmt

# Run pre-commit hooks on all files
pre-commit run --all-files
```

## Code Style Guidelines

- **Formatter/Linter**: Ruff (configured in `pyproject.toml`)
- **Type Checking**: Mypy (configured in `pyproject.toml`)
- **Pre-commit**: Use pre-commit hooks for consistent code style
- **Python Version**: Requires Python >=3.10

### Best Practices

- Use complete type annotations for all function signatures
- Use Sphinx-style docstrings (`:param:`, `:return:`, `:raises:`)
- Write tests for new functionality

## Key Files

- `src/sphinx_pytest/plugin.py` - Main pytest plugin with `sphinx_doctree` fixtures
- `src/sphinx_pytest/builders.py` - Custom `DoctreeBuilder` for testing

## Reference Documentation

- [Sphinx Repository](https://github.com/sphinx-doc/sphinx)
- [Sphinx Extension Development](https://www.sphinx-doc.org/en/master/extdev/index.html)
