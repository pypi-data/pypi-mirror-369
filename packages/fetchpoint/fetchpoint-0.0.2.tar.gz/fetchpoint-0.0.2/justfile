# Default recipe to show available commands
default:
    @just --list

# Clean all cache files
clean: clean-cache clean-tools

# Clean Python cache files
clean-cache:
    find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

# Clean tool cache directories
clean-tools:
    find . -type d -name '.*_cache' -exec rm -rf {} +

# Run ruff linter
lintify:
    uv run ruff check src

# Run ruff linter with auto-fix
lintify-fix:
    uv run ruff check --fix src

# Format code with ruff
prettify:
    uv run ruff format src

# Run type checking
type-check:
    uv run pyright src

# Run all validation steps
validate: lintify-fix prettify type-check test

# Run tests
test:
  uv run pytest src -vv
  # uv run pytest -ra -q -vv # pytest -ra -q -vv -n 8 -m 'not veryslow'

# Run tests with coverage
test-cov:
  uv run pytest src --cov=src --cov-report=term-missing

