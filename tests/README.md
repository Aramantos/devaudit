# DevAudit Tests

This directory contains the test suite for DevAudit.

## Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests (isolated components)
│   ├── auditors/            # Tests for auditor classes
│   │   ├── test_base_auditor.py
│   │   ├── test_python_audit.py
│   │   └── ...
│   └── server/              # Tests for server components
│       ├── test_history.py
│       └── ...
├── integration/             # Integration tests (multiple components)
│   └── test_full_scan.py
└── fixtures/                # Test data files (mock outputs, samples)
```

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### With Coverage
```bash
pytest --cov=devaudit --cov-report=html
```

### Specific Test File
```bash
pytest tests/unit/auditors/test_python_audit.py
```

### Verbose Output
```bash
pytest -v
```

## Writing Tests

### Unit Tests
- Test individual functions/classes in isolation
- Use mocks for external dependencies (subprocess, file I/O, APIs)
- Fast execution (no network calls, no file system operations)

### Integration Tests
- Test multiple components working together
- May use real file system (in temp directories)
- Test actual CLI commands and server endpoints

### Test Naming
- Test files: `test_*.py`
- Test functions: `test_*`
- Use descriptive names: `test_python_auditor_detects_vulnerabilities`

### Fixtures
- Shared fixtures in `conftest.py`
- Test-specific fixtures in individual test files
- Use `temp_dir` fixture for file operations

## Current Status

- ✅ Directory structure created
- ✅ Initial test files with TODO markers
- ⚠️ Most tests are skipped pending implementation
- ⚠️ Need to verify module imports and update accordingly

## Next Steps

1. Verify and fix module imports in test files
2. Implement unit tests for existing auditors
3. Add integration tests for CLI and dashboard
4. Set up CI/CD pipeline to run tests automatically
5. Aim for >70% code coverage

## Dependencies

Tests require additional packages (install with dev dependencies):
```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

Or install all dev dependencies:
```bash
pip install -e ".[dev]"
```
