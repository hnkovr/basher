# Command Executor

This project provides a Python script to execute bash commands with detailed logging and error handling.

## Features
- Execute single or multiline bash commands.
- Log command execution details.
- Switch between `loguru` and `logging` libraries.
- Configuration through a `Config` class.
- Integrated with development tools like `ruff`, `mypy`, `black`, `click`, `pylint`, `isort`, `docformatter`, `coverage`, and `pytest`.

## Requirements
- Python 3.10 or higher
- See `requirements.txt` for Python dependencies.

## Usage
```bash
# Execute a single command
python aaa.py

# Execute a multiline command
python aaa.py
```

## Development
### Setup
```bash
make install
```

### Linting
```bash
make lint
```

### Testing
```bash
make test
```

### Coverage
```bash
make coverage
```

### Formatting
```bash
make format
```

### Type Checking
```bash
make type-check
```

## Docker
### Build
```bash
docker build -t command-executor .
```

### Run
```bash
docker run --rm command-executor
```
