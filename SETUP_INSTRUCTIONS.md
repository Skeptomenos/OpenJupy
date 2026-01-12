# OpenCode Jupyter Integration - Setup Instructions

This guide explains how to integrate Jupyter Notebook capabilities into OpenCode using `jupyter-mcp-server`.

## Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) package manager
- OpenCode installed and configured

## Step 1: Install JupyterLab Environment

Install the required Jupyter packages with specific versions for RTC (Real-Time Collaboration) stability:

```bash
pip install jupyterlab==4.4.1 jupyter-collaboration==4.0.2 ipykernel

# Fix pycrdt version conflict (required for RTC)
pip uninstall -y pycrdt datalayer_pycrdt
pip install datalayer_pycrdt==0.12.17
```

## Step 2: Start JupyterLab

Start JupyterLab with a token for authentication:

```bash
# Generate a secure token or use a fixed one for development
export JUPYTER_TOKEN="your-secure-token-here"

jupyter lab --port 8888 --IdentityProvider.token "$JUPYTER_TOKEN" --ip 0.0.0.0
```

**Note**: Keep this terminal running. JupyterLab must be active for the MCP server to connect.

## Step 3: Configure OpenCode

Add the following to your `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "jupyter": {
      "type": "local",
      "command": ["uvx", "jupyter-mcp-server@latest"],
      "enabled": true,
      "timeout": 30000,
      "environment": {
        "JUPYTER_URL": "http://localhost:8888",
        "JUPYTER_TOKEN": "{env:JUPYTER_TOKEN}",
        "ALLOW_IMG_OUTPUT": "true"
      }
    }
  }
}
```

**Important**: Set the `JUPYTER_TOKEN` environment variable in your shell before starting OpenCode:

```bash
export JUPYTER_TOKEN="your-secure-token-here"
```

## Step 4: Configure Data-Scientist Agent (Optional)

To avoid context bloat from 14+ Jupyter tools in every conversation, create a specialized agent.

Add the following to your `~/.config/opencode/oh-my-opencode.json`:

```json
{
  "agent": {
    "data-scientist": {
      "name": "Data Scientist",
      "model": "google-vertex-anthropic/claude-opus-4-5@20251101",
      "temperature": 0.2,
      "system": "You are a senior data scientist and ML engineer. Use Jupyter tools for all analysis, visualization, and model development. Maintain persistent state across cells.",
      "permission": {
        "edit": "allow",
        "bash": "allow"
      },
      "tools": {
        "jupyter_*": true,
        "bash": true,
        "read": true
      }
    }
  }
}
```

Then disable Jupyter tools globally to keep them out of other agents:

```json
{
  "tools": {
    "jupyter_*": false
  }
}
```

## Step 5: Verify Installation

Run the validation script to check your setup:

```bash
python validate_jupyter_setup.py
```

Or manually test in OpenCode:

```
Use jupyter to create a new notebook called test.ipynb and add a cell that prints "Hello World"
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `JUPYTER_URL` | URL of your JupyterLab server | Yes |
| `JUPYTER_TOKEN` | Authentication token for Jupyter | Yes |
| `ALLOW_IMG_OUTPUT` | Enable image/plot output in responses | Recommended |

## Troubleshooting

### "Connection refused" errors

Ensure JupyterLab is running on the configured port:

```bash
jupyter lab list
```

### Token mismatch

Verify the token matches between JupyterLab and your environment:

```bash
echo $JUPYTER_TOKEN
```

### RTC sync issues

If real-time sync isn't working, verify `jupyter-collaboration` is installed:

```bash
pip show jupyter-collaboration
```

### Kernel not found

Register a Python kernel if none exists:

```bash
python -m ipykernel install --user --name python3
```

## Available Jupyter Tools

Once configured, the following tools become available:

| Tool | Description |
|------|-------------|
| `use_notebook` | Connect to or create a notebook |
| `list_notebooks` | List managed notebooks |
| `read_notebook` | Read notebook cells |
| `insert_cell` | Insert new code/markdown cell |
| `execute_cell` | Execute a cell |
| `execute_code` | Execute code directly |
| `restart_notebook` | Restart kernel |
| `list_kernels` | List available kernels |
| `list_files` | List files in Jupyter filesystem |

## Verifying Real-Time Sync

To verify that RTC (Real-Time Collaboration) is working:

1. Open JupyterLab in your browser at `http://localhost:8888`
2. Create or open a notebook
3. In OpenCode, use the Jupyter tools to add a cell to the same notebook
4. The cell should appear in your browser within 2 seconds

If sync is not working, check:
- `jupyter-collaboration` is installed: `pip show jupyter-collaboration`
- `datalayer_pycrdt` version is correct: `pip show datalayer_pycrdt` (should be 0.12.17)

## Security Notes

1. **Never commit tokens**: Add `JUPYTER_TOKEN` to your `.env` file, not config files
2. **Use strong tokens**: Generate random tokens for production use
3. **Bind to localhost**: Use `--ip 127.0.0.1` instead of `0.0.0.0` for local-only access
