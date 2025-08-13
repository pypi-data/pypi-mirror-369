# Release Guide

This guide explains how to release new versions of bankinter-converter to PyPI using Trusted Publishers.

## Prerequisites

1. **PyPI Account**: Create an account at [PyPI](https://pypi.org/account/register/)
2. **Trusted Publisher Setup**: Configure a trusted publisher on PyPI for this repository

## Setting Up Trusted Publishers

### 1. Create PyPI Project (if not exists)
- Go to [PyPI](https://pypi.org/manage/projects/)
- Create a new project named `bankinter-converter`

### 2. Add Trusted Publisher
- In your PyPI project settings, go to "Trusted Publishers"
- Add a new trusted publisher with these settings:
  - **Publisher**: `github`
  - **Owner**: `barbarity`
  - **Repository**: `bankinter-converter`
  - **Workflow name**: `release.yml`
  - **Environment name**: (leave empty)

This allows PyPI to trust releases from your GitHub Actions workflow automatically.

## Release Process

### 1. Prepare the Release

```bash
# Update version using the release script
python scripts/release.py 0.2.0

# Or manually update version in pyproject.toml
# version = "0.2.0"
```

### 2. Test Locally

```bash
# Install dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Check code quality
uv run ruff check .

# Test the build
uv build
```

### 3. Commit and Tag

```bash
# Commit changes
git add .
git commit -m "Release 0.2.0"

# Create and push tag
git tag v0.2.0
git push origin v0.2.0
```

### 4. Automated Release

Once you push the tag, GitHub Actions will automatically:

1. Run all tests
2. Check code quality
3. Build the package
4. Publish to PyPI (using Trusted Publishers)
5. Create a GitHub release

## Installation Methods

After publishing to PyPI, users can install your package using:

### uvx (Recommended)
```bash
# Run directly
uvx bankinter-converter --help

# Install globally
uvx install bankinter-converter
```

### uv
```bash
# Install globally
uv tool install bankinter-converter
```

### pip
```bash
pip install bankinter-converter
```

## Version Management

- **Patch releases** (0.1.1): Bug fixes
- **Minor releases** (0.2.0): New features, backward compatible
- **Major releases** (1.0.0): Breaking changes

## Troubleshooting

### PyPI Publishing Fails
- Check that Trusted Publisher is properly configured on PyPI
- Verify the workflow name matches exactly: `Release to PyPI`
- Ensure the repository owner and name are correct
- Check that the tag format is correct (e.g., `v0.1.0`)

### Tests Fail
- Run tests locally before tagging
- Check that all dependencies are properly specified
- Verify Python version compatibility

### Build Fails
- Ensure `pyproject.toml` is properly formatted
- Check that all required fields are present
- Verify the package structure is correct

## Benefits of Trusted Publishers

- **No API tokens needed**: No manual token creation or management
- **Enhanced security**: Short-lived tokens that expire automatically
- **Simplified setup**: Only need to configure the trusted publisher once
- **Automatic verification**: PyPI verifies the GitHub Actions context
- **No secrets management**: No need to store sensitive tokens in GitHub secrets
