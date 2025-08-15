# Language Balls

Animated language balls moving at different periods based on performance benchmarks.

## Installation

```bash
pip install language-balls
```

## Usage

```bash
language-balls
```

## Deployment to PyPI

### Prerequisites
1. Create account at https://pypi.org/account/register/
2. Generate API token:
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Set scope to "Entire account" or specific project
   - Copy the token (starts with `pypi-`)
3. For test PyPI (optional):
   - Create account at https://test.pypi.org/account/register/
   - Generate token at https://test.pypi.org/manage/account/token/

### Setup .pypirc (optional)
Create `~/.pypirc` file:
```ini
[distutils]
index-servers = pypi testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### Commands
```bash
# Install deployment tools
pip install build twine

# Build packages
python -m build

# Upload to PyPI (credentials from .pypirc)
twine upload dist/*

# Or upload to test PyPI first
twine upload --repository testpypi dist/*
```

### Notes
- The build creates both wheel (.whl) and source (.tar.gz) distributions in the `dist/` folder
- With `.pypirc` configured, twine will use stored credentials automatically
- Use `--repository testpypi` to test on test.pypi.org first