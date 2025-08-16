# Publishing Monkeybox to PyPI

This guide provides step-by-step instructions for publishing the monkeybox package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts at:
   - Production: https://pypi.org/account/register/
   - Test: https://test.pypi.org/account/register/

2. **API Tokens**: Generate API tokens for secure upload:
   - Go to Account Settings → API tokens
   - Create a token with "Entire account" scope initially
   - After first upload, create project-specific tokens

3. **Install Build Tools**:
   ```bash
   uv add --dev build twine
   ```

## Pre-Publishing Checklist

Before publishing, ensure:

- [ ] All tests pass: `uv run pytest --cov-fail-under=90`
- [ ] Code is formatted: `uv run ruff format .`
- [ ] Code passes linting: `uv run ruff check .`
- [ ] Type checking passes: `uv run ty check src/monkeybox`
- [ ] Version is updated in `pyproject.toml`
- [ ] CHANGELOG is updated (if you have one)
- [ ] Documentation is current
- [ ] LICENSE file exists

## Building the Package

1. **Clean previous builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

2. **Build the distribution**:
   ```bash
   uv run python -m build
   ```

   This creates:
   - `dist/monkeybox-{version}.tar.gz` (source distribution)
   - `dist/monkeybox-{version}-py3-none-any.whl` (wheel)

3. **Verify the build**:
   ```bash
   uv run twine check dist/*
   ```

## Testing with TestPyPI

Always test with TestPyPI first:

1. **Upload to TestPyPI**:
   ```bash
   uv run twine upload --repository testpypi dist/*
   ```

   When prompted, use:
   - Username: `__token__`
   - Password: Your TestPyPI API token

2. **Test installation**:
   ```bash
   # In a new virtual environment
   uv venv test-env
   source test-env/bin/activate  # On Windows: test-env\Scripts\activate

   # Install from TestPyPI
   uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ monkeybox

   # Test the package
   python -c "from monkeybox import Agent, OpenAIModel; print('Import successful!')"
   ```

## Publishing to PyPI

Once testing is successful:

1. **Upload to PyPI**:
   ```bash
   uv run twine upload dist/*
   ```

   When prompted, use:
   - Username: `__token__`
   - Password: Your PyPI API token

2. **Verify the release**:
   - Check https://pypi.org/project/monkeybox/
   - Install and test: `uv pip install monkeybox`

## Automating with GitHub Actions

For automated releases, add this workflow to `.github/workflows/publish.yml`:

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
        python-version: '3.11'

    - name: Install uv
      uses: astral-sh/setup-uv@v3

    - name: Install dependencies
      run: |
        uv sync
        uv add --dev build twine

    - name: Run tests
      run: |
        uv run pytest --cov-fail-under=90

    - name: Build package
      run: |
        uv run python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        uv run twine upload dist/*
```

Add your PyPI API token to GitHub repository secrets as `PYPI_API_TOKEN`.

## Version Management

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Update version in `pyproject.toml`:
```toml
[project]
version = "0.2.0"  # Update this
```

## Post-Publishing

After successful publication:

1. **Create a Git tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

2. **Create GitHub Release**:
   - Go to Releases → Create new release
   - Choose the tag
   - Add release notes
   - Publish release

3. **Update project token**:
   - Create a project-specific API token on PyPI
   - Replace the general token for future uploads

## Troubleshooting

### Common Issues

1. **"Invalid distribution file"**:
   - Ensure `twine check dist/*` passes
   - Rebuild the package

2. **"Package name already taken"**:
   - Choose a unique name in `pyproject.toml`
   - Check availability at https://pypi.org/project/{name}/

3. **"Invalid classifier"**:
   - Verify classifiers against https://pypi.org/classifiers/

4. **Missing dependencies on install**:
   - Ensure all dependencies are listed in `pyproject.toml`
   - Test installation in clean environment

## Security Notes

- **Never commit tokens** to version control
- Use **project-specific tokens** after first upload
- Rotate tokens regularly
- Enable 2FA on PyPI account

## Additional Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging User Guide](https://packaging.python.org/)
