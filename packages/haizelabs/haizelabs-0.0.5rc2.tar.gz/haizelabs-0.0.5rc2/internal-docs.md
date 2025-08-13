This document contains internal development guidelines for the Haize SDK.

## Development Setup

### Prerequisites

- Python 3.10
- uv (recommended) or pip
- git

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/haizelabs/haizelabs-sdk.git
cd haizelabs-sdk
```

2. Create a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. Install the SDK in editable/development mode. This makes sure the `haizelabs` library reflects your local code and optional dev dependencies are installed.
```bash
uv pip install -e ".[dev]"
```

### Installing Dependencies

The project uses `uv` for dependency management. Dependencies are specified in `pyproject.toml`.

To install all dependencies including development tools:
```bash
uv pip install -e ".[dev]"
```

This installs:
- Core dependencies (httpx, pydantic, etc.)
- Testing tools (pytest, pytest-asyncio, vcrpy)
- Linting tools (black, ruff, mypy)
- Pre-commit hooks

## Testing

### Running Tests

Run all tests:
```bash
python -m pytest
```

Run specific test file:
```bash
python -m pytest tests/test_judges.py
```

Run with verbose output:
```bash
python -m pytest -v
```

Run specific test function:
```bash
python -m pytest tests/test_judges.py::test_judges_create_exact_match
```

### Test Cassettes

We use VCR.py to record and replay HTTP interactions for tests. This allows tests to run without hitting the actual API.

**Recording new cassettes:**
1. Set your API key: `export HAIZE_API_KEY=your-key`
2. Delete the existing cassette if updating
3. Run the test to record new interactions
4. Commit the new cassette file

**Cassette location:** `cassettes/` directory

**Important notes:**
- Cassettes record actual API responses
- Sensitive data (API keys) are automatically filtered


## Pre-commit Hooks

**Setup:**
```bash
.venv/bin/pre-commit install
```

**Hooks configured:**
1. **Black** - Python code formatter
2. **Ruff** - Python linter with auto-fix
3. **detect-secrets** - Scans for potential secrets/credentials

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md (if exists)
3. Create a git tag:
   ```bash
   git tag v0.0.5
   git push origin v0.0.5
   ```
4. Build the package:
   ```bash
   python -m build
   ```
5. Upload to PyPI (when ready):
   ```bash
   python -m twine upload dist/*
   ```
