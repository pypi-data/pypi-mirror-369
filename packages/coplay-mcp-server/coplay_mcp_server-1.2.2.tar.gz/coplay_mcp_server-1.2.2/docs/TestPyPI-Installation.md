# Installing from Test PyPI with Mixed Dependencies

When installing from Test PyPI, you may encounter dependency version mismatches. Here are the recommended approaches:

## Method 1: Mixed Index Installation (Recommended)

Install your package from Test PyPI but allow dependencies to come from main PyPI:

```bash
# Using pip
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ coplay-mcp-server

# Using uvx
uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ coplay-mcp-server
```

## Method 2: Install Dependencies First

Pre-install dependencies from main PyPI, then install your package from Test PyPI:

```bash
# Install dependencies from main PyPI first
pip install aiofiles>=24.1.0 anyio>=4.10.0 mcp[cli]>=1.12.4 psutil>=7.0.0 pydantic>=2.11.7 watchdog>=6.0.0

# Then install your package from Test PyPI (will skip already satisfied dependencies)
pip install --index-url https://test.pypi.org/simple/ --no-deps coplay-mcp-server
```

## Method 3: Using uv (Modern Python Package Manager)

If you're using `uv`, you can specify multiple indexes:

```bash
# Add both indexes to uv
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ coplay-mcp-server
```

## Method 4: Temporary Requirements File

Create a temporary requirements file for testing:

```bash
# Create test-requirements.txt
echo "--index-url https://test.pypi.org/simple/" > test-requirements.txt
echo "--extra-index-url https://pypi.org/simple/" >> test-requirements.txt
echo "coplay-mcp-server" >> test-requirements.txt

# Install using the requirements file
pip install -r test-requirements.txt
```

## Verification

After installation, verify everything works:

```bash
# Test the CLI
coplay-mcp-server --help

# Test Python import
python -c "import coplay_mcp_server; print('Import successful')"

# Check installed version
pip show coplay-mcp-server
