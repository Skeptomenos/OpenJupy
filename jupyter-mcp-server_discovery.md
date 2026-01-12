# Jupyter MCP Server Discovery Report

**Date**: January 11, 2026  
**Analyst**: Sisyphus (OpenCode Agent)  
**Repository**: https://github.com/datalayer/jupyter-mcp-server  
**Package Name**: `jupyter-mcp-server`  
**Version**: 0.17.1 (latest)  
**Organization**: Datalayer, Inc.  
**License**: BSD 3-Clause  

---

## Executive Summary

Jupyter MCP Server is a **production-grade**, actively maintained MCP server for Jupyter notebook integration. Developed by Datalayer (a company focused on Jupyter infrastructure), it provides real-time notebook manipulation, multi-notebook support, and dual-mode operation (standalone MCP server or Jupyter extension).

**Overall Assessment**: Excellent. Ready for OpenCode integration with minimal modifications.

| Aspect | Rating | Notes |
|--------|--------|-------|
| Architecture | 5/5 | Dual-mode, clean separation, well-documented |
| MCP Integration | 5/5 | FastMCP, proper tool annotations, streaming support |
| Code Quality | 5/5 | Type hints, linting, comprehensive error handling |
| Documentation | 5/5 | Dedicated docs site, architecture docs, examples |
| Testing | 4/5 | pytest suite, integration tests |
| Community | 5/5 | 841 stars, 136 forks, 18 open issues, active development |
| Production Readiness | 5/5 | Docker support, PyPI published, used in production |

---

## Project Overview

### What It Does

Jupyter MCP Server enables AI assistants to:

1. **Execute code** in Jupyter kernels with real-time output streaming
2. **Manage notebooks** - create, read, edit cells, switch between notebooks
3. **Handle multimodal output** - images, plots, rich text
4. **Integrate with JupyterLab** - automatic notebook opening, RTC sync
5. **Connect to any Jupyter deployment** - local, JupyterHub, cloud

### Key Statistics

| Metric | Value |
|--------|-------|
| Stars | 841 |
| Forks | 136 |
| Open Issues | 18 |
| Contributors | 10+ |
| Last Commit | January 9, 2026 |
| PyPI Downloads | Active (badge shows significant usage) |
| Docker Pulls | Active |

### Top Contributors

1. eleonorecharles - 69 contributions
2. echarles (Eric Charles) - 54 contributions
3. ChengJiale150 - 32 contributions
4. Plus community contributors

---

## Architecture

### Dual-Mode Operation

```
┌─────────────────────────────────────────────────────────────────┐
│                       MCP Client (OpenCode)                     │
└────────────┬────────────────────────────────────┬───────────────┘
             │ stdio                              │ HTTP/SSE
             │                                    │
    ┌────────▼────────────┐          ┌───────────▼──────────────┐
    │   MCP_SERVER Mode   │          │  JUPYTER_SERVER Mode     │
    │   (Standalone)      │          │  (Extension)             │
    │                     │          │                          │
    │   - uvx/pip install │          │  - Jupyter extension     │
    │   - Connects via    │          │  - Direct API access     │
    │     HTTP/WebSocket  │          │  - Zero network overhead │
    └──────────┬──────────┘          └──────────┬───────────────┘
               │                                │
               └────────────┬───────────────────┘
                            │
                   ┌────────▼────────┐
                   │  Tool Layer     │
                   │  (14 tools)     │
                   └────────┬────────┘
                            │
                   ┌────────▼────────┐
                   │ Jupyter Server  │
                   │ (local/remote)  │
                   └─────────────────┘
```

### Mode Selection

| Mode | Use Case | Transport | Performance |
|------|----------|-----------|-------------|
| **MCP_SERVER** | Standalone, connects to remote Jupyter | stdio or streamable-http | Good |
| **JUPYTER_SERVER** | Embedded in Jupyter Server | Direct API | Excellent |

For OpenCode, **MCP_SERVER mode with stdio transport** is the correct choice.

---

## Tool Inventory

### Server Management (2 tools)

| Tool | Description | Read-Only |
|------|-------------|-----------|
| `list_files` | List files/directories in Jupyter filesystem | Yes |
| `list_kernels` | List available and running kernels | Yes |

### Multi-Notebook Management (5 tools)

| Tool | Description | Destructive |
|------|-------------|-------------|
| `use_notebook` | Connect to/create notebook, activate for operations | Yes |
| `list_notebooks` | List all managed notebooks | No |
| `restart_notebook` | Restart kernel for a notebook | Yes |
| `unuse_notebook` | Disconnect from notebook, release resources | Yes |
| `read_notebook` | Read notebook cells (brief or detailed format) | No |

### Cell Operations (7 tools)

| Tool | Description | Destructive |
|------|-------------|-------------|
| `read_cell` | Read single cell content and outputs | No |
| `insert_cell` | Insert new code/markdown cell | Yes |
| `delete_cell` | Delete cells by index | Yes |
| `overwrite_cell_source` | Modify cell content (returns diff) | Yes |
| `execute_cell` | Execute cell with timeout, streaming support | Yes |
| `insert_execute_code_cell` | Insert and execute in one step | Yes |
| `execute_code` | Execute code directly (not saved to notebook) | Yes |

### Prompts (1 prompt)

| Prompt | Description |
|--------|-------------|
| `jupyter-cite` | Cite specific cells from notebook (like @ in IDEs) |

**Total**: 14 tools + 1 prompt

---

## Dependencies

```toml
dependencies = [
    "jupyter-kernel-client>=0.7.3",
    "jupyter-mcp-tools>=0.1.6",
    "jupyter-nbmodel-client>=0.14.4",
    "jupyter-server-nbmodel>=0.1.1a4",
    "jupyter-server-client",
    "jupyter_server>=1.6,<3",
    "tornado>=6.1",
    "traitlets>=5.0",
    "mcp[cli]>=1.10.1",
    "pydantic",
    "uvicorn",
    "click",
    "fastapi"
]
```

**Assessment**: 
- All dependencies are well-maintained Jupyter ecosystem packages
- No bloated ML libraries (unlike ClaudeJupy)
- `mcp[cli]` provides official MCP SDK
- FastAPI/uvicorn for HTTP transport option

---

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JUPYTER_URL` | Jupyter server URL (shorthand) | `http://localhost:8888` |
| `JUPYTER_TOKEN` | Jupyter auth token (shorthand) | None |
| `DOCUMENT_URL` | Document server URL | Falls back to JUPYTER_URL |
| `DOCUMENT_TOKEN` | Document auth token | Falls back to JUPYTER_TOKEN |
| `RUNTIME_URL` | Kernel/runtime URL | Falls back to JUPYTER_URL |
| `RUNTIME_TOKEN` | Runtime auth token | Falls back to JUPYTER_TOKEN |
| `DOCUMENT_ID` | Default notebook path | None (interactive selection) |
| `ALLOW_IMG_OUTPUT` | Enable image output | `true` |
| `TRANSPORT` | Transport type | `stdio` |
| `PORT` | HTTP port (for streamable-http) | `4040` |
| `JUPYTERLAB` | Enable JupyterLab mode | `true` |
| `ALLOWED_JUPYTER_MCP_TOOLS` | Comma-separated tool whitelist | `notebook_run-all-cells,notebook_get-selected-cell` |

### CLI Options

```bash
jupyter-mcp-server \
  --transport stdio \
  --jupyter-url http://localhost:8888 \
  --jupyter-token MY_TOKEN \
  --document-id notebook.ipynb \
  --jupyterlab true
```

---

## OpenCode Integration

### Feasibility Assessment

| Requirement | Support | Notes |
|-------------|---------|-------|
| Local MCP server | Yes | stdio transport |
| Command-based startup | Yes | `uvx jupyter-mcp-server` |
| Environment variables | Yes | Full support |
| Tool registration | Yes | FastMCP with annotations |
| Timeout support | Yes | Per-tool and global |
| Multimodal output | Yes | Images, plots |

### Proposed OpenCode Configuration

```json
{
  "mcp": {
    "jupyter": {
      "type": "local",
      "command": [
        "uvx",
        "jupyter-mcp-server@latest"
      ],
      "enabled": true,
      "timeout": 30000,
      "environment": {
        "JUPYTER_URL": "http://localhost:8888",
        "JUPYTER_TOKEN": "YOUR_TOKEN",
        "ALLOW_IMG_OUTPUT": "true"
      }
    }
  }
}
```

### Alternative: Docker

```json
{
  "mcp": {
    "jupyter": {
      "type": "local",
      "command": [
        "docker", "run", "-i", "--rm",
        "-e", "JUPYTER_URL",
        "-e", "JUPYTER_TOKEN",
        "-e", "ALLOW_IMG_OUTPUT",
        "datalayer/jupyter-mcp-server:latest"
      ],
      "enabled": true,
      "environment": {
        "JUPYTER_URL": "http://host.docker.internal:8888",
        "JUPYTER_TOKEN": "YOUR_TOKEN",
        "ALLOW_IMG_OUTPUT": "true"
      }
    }
  }
}
```

### Context Token Impact

- **Tools registered**: 14
- **Tokens per tool**: ~300-500 (well-documented with annotations)
- **Total overhead**: ~5,000-7,000 tokens

**Recommendation**: Acceptable overhead. Use tool filtering if needed:

```json
{
  "tools": {
    "jupyter_*": false
  },
  "agent": {
    "data-science": {
      "tools": {
        "jupyter_*": true
      }
    }
  }
}
```

---

## Strengths

### 1. Production-Grade Quality

- Published on PyPI with proper versioning
- Docker images available
- Comprehensive documentation site
- Active issue tracking and resolution
- BSD 3-Clause license (permissive)

### 2. Dual-Mode Architecture

- Can run standalone (MCP_SERVER) or embedded (JUPYTER_SERVER)
- Automatic backend selection based on configuration
- Supports both local and remote Jupyter servers

### 3. Real-Time Collaboration Support

- Integrates with Jupyter's Y.js-based RTC
- Changes sync in real-time with JupyterLab UI
- Supports collaborative editing scenarios

### 4. Comprehensive Tool Set

- 14 well-designed tools covering all notebook operations
- Proper tool annotations (readOnlyHint, destructiveHint)
- Streaming execution with progress updates
- Multimodal output support (images, plots)

### 5. Excellent Error Handling

- `safe_notebook_operation()` wrapper with retry logic
- Timeout handling with kernel interrupt
- Graceful degradation when features unavailable

### 6. Active Development

- Last commit: January 9, 2026 (2 days ago)
- Regular releases and dependency updates
- Responsive to community issues

---

## Potential Issues

### Minor Issues

| Issue | Severity | Impact | Mitigation |
|-------|----------|--------|------------|
| Requires running Jupyter server | Low | Need to start JupyterLab separately | Document in setup |
| RTC dependency for some features | Low | Some features need jupyter-collaboration | Optional, graceful fallback |
| 18 open issues | Low | Active project, issues being addressed | None needed |

### Known Open Issues (from GitHub)

1. **#183**: XSRF-protected Jupyter deployments - workaround available
2. **#181**: Multi-user serving on hosted JupyterLab - in discussion
3. **#160**: Stuck execution with PYTHONDEVMODE=1 - edge case
4. **#146**: UI edits stop syncing after MCP edits - RTC sync issue

**Assessment**: None of these are blockers for OpenCode integration. All are edge cases or feature requests.

---

## Comparison: jupyter-mcp-server vs ClaudeJupy

| Aspect | jupyter-mcp-server | ClaudeJupy |
|--------|-------------------|------------|
| **Maturity** | Production (841 stars) | Early (3 commits) |
| **Organization** | Datalayer (company) | Individual |
| **Dependencies** | Minimal, focused | Bloated (PyTorch) |
| **Architecture** | Dual-mode, clean | Single-mode |
| **Documentation** | Excellent (docs site) | Good (README) |
| **Testing** | pytest suite | Minimal |
| **Docker** | Yes | No |
| **PyPI** | Yes | Yes |
| **Active Development** | Very active | Just started |
| **Issues to Fix** | None critical | Several critical |

**Recommendation**: Use jupyter-mcp-server. It's the clear winner.

---

## Pre-Integration Checklist

### Prerequisites

- [ ] JupyterLab 4.4.1 installed
- [ ] jupyter-collaboration 4.0.2 installed (for RTC)
- [ ] jupyter-mcp-tools >= 0.1.4 installed
- [ ] UV installed (`pip install uv`)

### Setup Steps

1. **Install JupyterLab environment**:
   ```bash
   pip install jupyterlab==4.4.1 jupyter-collaboration==4.0.2 jupyter-mcp-tools>=0.1.4 ipykernel
   pip uninstall -y pycrdt datalayer_pycrdt
   pip install datalayer_pycrdt==0.12.17
   ```

2. **Start JupyterLab**:
   ```bash
   jupyter lab --port 8888 --IdentityProvider.token MY_TOKEN --ip 0.0.0.0
   ```

3. **Add to OpenCode config** (`~/.config/opencode/opencode.json`):
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
           "JUPYTER_TOKEN": "MY_TOKEN",
           "ALLOW_IMG_OUTPUT": "true"
         }
       }
     }
   }
   ```

4. **Test in OpenCode**:
   ```
   Use jupyter to create a new notebook called test.ipynb and add a cell that prints "Hello World"
   ```

---

## Conclusion

**jupyter-mcp-server** is an excellent choice for OpenCode integration:

1. **No modifications needed** - Works out of the box
2. **Production-ready** - Used by real users, actively maintained
3. **Well-documented** - Comprehensive docs, architecture guide
4. **Clean dependencies** - No bloat, focused on Jupyter ecosystem
5. **Active community** - Issues addressed, features added regularly

**Recommendation**: Integrate directly without forking. The project is mature enough that forking would create unnecessary maintenance burden. Simply add the configuration to OpenCode and document the JupyterLab setup requirements.

**Estimated Integration Effort**: 30 minutes (config + testing)

---

## Appendix: File Structure

```
jupyter_mcp_server/
├── CLI.py                      # Command-line interface
├── server.py                   # FastMCP server, tool registration
├── config.py                   # Configuration management
├── notebook_manager.py         # Multi-notebook lifecycle
├── server_context.py           # Mode detection, client management
├── utils.py                    # Execution utilities
├── enroll.py                   # Auto-enrollment system
├── models.py                   # Pydantic data models
├── log.py                      # Logging configuration
├── tool_cache.py               # Tool caching for performance
│
├── tools/                      # Tool implementations
│   ├── _base.py               # BaseTool, ServerMode enum
│   ├── list_files_tool.py
│   ├── list_kernels_tool.py
│   ├── use_notebook_tool.py
│   ├── list_notebooks_tool.py
│   ├── restart_notebook_tool.py
│   ├── unuse_notebook_tool.py
│   ├── read_notebook_tool.py
│   ├── read_cell_tool.py
│   ├── insert_cell_tool.py
│   ├── delete_cell_tool.py
│   ├── overwrite_cell_source_tool.py
│   ├── execute_cell_tool.py
│   ├── execute_code_tool.py
│   └── jupyter_cite_prompt.py
│
└── jupyter_extension/          # Jupyter Server extension
    ├── extension.py
    ├── handlers.py
    ├── context.py
    └── backends/
        ├── base.py
        ├── local_backend.py
        └── remote_backend.py
```

---

## References

- **Documentation**: https://jupyter-mcp-server.datalayer.tech/
- **GitHub**: https://github.com/datalayer/jupyter-mcp-server
- **PyPI**: https://pypi.org/project/jupyter-mcp-server/
- **Docker Hub**: https://hub.docker.com/r/datalayer/jupyter-mcp-server
- **MCP Specification**: https://modelcontextprotocol.io/specification
