# PyPI Publishing Guide for FetchPoint

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **API Token**: Generate a token at https://pypi.org/manage/account/token/
   - Scope: Can be project-specific or for entire account
   - Save the token securely (starts with `pypi-`)

## Publishing Steps

### 1. Prepare Your Environment

```bash
# Ensure you have the latest uv
pip install --upgrade uv

# Clean any previous builds
rm -rf dist/
```

### 2. Update Version

Edit the version in `src/fetchpoint/__init__.py`:

```python
__version__ = "0.1.0"  # Increment as needed
```

Follow semantic versioning:

- MAJOR.MINOR.PATCH (e.g., 1.0.0)
- MAJOR: Breaking API changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### 3. Validate Your Code

```bash
# Run the complete validation suite
just validate

# Or manually:
uv run ruff format src
uv run ruff check --fix src
uv run pyright src
uv run pytest src -vv
```

### 4. Build Distribution Packages

```bash
# Build wheel (binary distribution)
uv build --wheel

# Build source distribution
uv build --sdist

# Verify the files were created
ls -la dist/
```

You should see:

- `fetchpoint-X.Y.Z-py3-none-any.whl` (wheel)
- `fetchpoint-X.Y.Z.tar.gz` (source distribution)

### 5. Test with TestPyPI (Optional but Recommended)

TestPyPI is a separate instance for testing:

```bash
# Get a TestPyPI token from https://test.pypi.org/manage/account/token/
export TEST_PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcC..."

# Upload to TestPyPI
uv publish --repository testpypi --token $TEST_PYPI_TOKEN

# Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps fetchpoint
```

### 6. Publish to PyPI

```bash
# Set your PyPI token
export PYPI_TOKEN="pypi-AgEIcHlwaS5vcmcC..."

# Publish to PyPI
uv publish --token $PYPI_TOKEN
```

### 7. Verify Publication

1. Check your package at: https://pypi.org/project/fetchpoint/
2. Test installation:
   ```bash
   pip install fetchpoint
   ```

## Important Notes

### Version Management

- **Cannot Overwrite**: Once a version is published, it cannot be changed
- **Must Increment**: Always increment version for new releases
- **Delete Protection**: Deleted versions cannot be reused

### Security

- **Never commit tokens** to version control
- Use environment variables or secure credential storage
- Consider using GitHub Actions for automated publishing

### Package Naming

- Package name must be unique on PyPI
- Check availability at https://pypi.org/project/YOUR-PACKAGE-NAME/

### Common Issues

1. **Name Already Taken**: Choose a different package name
2. **Invalid Metadata**: Ensure pyproject.toml has all required fields
3. **Authentication Failed**: Check token is correct and has proper scope
4. **Version Already Exists**: Increment version number

## Automation with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install uv
        run: pip install uv
      - name: Build package
        run: |
          uv build --wheel
          uv build --sdist
      - name: Publish to PyPI
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: uv publish --token $PYPI_TOKEN
```

Add your PyPI token as a GitHub secret named `PYPI_TOKEN`.

## Quick Reference

```bash
# Complete publishing workflow
just validate                    # Validate code
uv build --wheel && uv build --sdist  # Build packages
uv publish --token $PYPI_TOKEN   # Publish to PyPI
```

## Resources

- [PyPI Documentation](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Classifiers List](https://pypi.org/classifiers/)
