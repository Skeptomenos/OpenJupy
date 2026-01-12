# ClaudeJupy Discovery Report

**Date**: January 11, 2026  
**Analyst**: Sisyphus (OpenCode Agent)  
**Repository**: https://github.com/mayank-ketkar-sf/ClaudeJupy  
**Package Name**: `ml-jupyter-mcp`  
**Version**: 2.0.0  
**Author**: Mayank Ketkar  

---

## Executive Summary

ClaudeJupy is an MCP (Model Context Protocol) server that provides persistent Jupyter kernel execution capabilities for Claude-based AI assistants. The project demonstrates solid architecture and thoughtful Claude-specific integrations, but contains critical dependency issues that must be resolved before production use.

**Overall Assessment**: Good foundation, needs cleanup before OpenCode integration.

| Aspect | Rating | Notes |
|--------|--------|-------|
| Architecture | 4/5 | Clean modular design |
| MCP Integration | 4/5 | Proper FastMCP usage |
| Error Handling | 5/5 | Excellent Claude-specific guidance |
| Production Readiness | 2/5 | Critical dependency issues |
| Documentation | 4/5 | Clear README and docstrings |
| Testing | 2/5 | Minimal actual tests |

---

## Project Overview

### What It Does

ClaudeJupy provides an MCP server that allows AI assistants to:

1. **Execute Python code** with persistent state across conversations
2. **Manage Jupyter notebooks** (create, edit, add cells)
3. **Handle errors intelligently** with actionable fix suggestions
4. **Manage Python environments** via UV package manager
5. **Debug and profile** code execution

### Architecture

```
src/ml_jupyter_mcp/
├── server.py           # FastMCP server entry point
├── daemon/
│   ├── client.py       # Kernel communication wrapper
│   └── kernel_daemon.py.old  # Dead code
├── kernel/
│   └── manager.py      # SimpleKernelManager using jupyter_client
├── handlers/
│   ├── error_handler.py    # Smart error parsing with suggestions
│   └── response.py         # Response formatting
├── tools/
│   ├── execution.py    # Code execution tools
│   ├── environment.py  # UV environment management
│   ├── notebook.py     # Notebook CRUD operations
│   ├── debugging.py    # Variable inspection, profiling
│   └── guidance.py     # Claude-specific help system
├── environment/        # UV/venv detection (referenced but not visible)
└── setup/              # Kernel registration utilities
```

### Key Technologies

- **FastMCP**: MCP server framework
- **jupyter_client**: Standard Jupyter kernel management
- **nbformat**: Notebook file manipulation
- **UV**: Modern Python package manager (preferred over pip)

---

## Strengths

### 1. Clean Modular Architecture

The codebase follows good separation of concerns:
- Tools are organized by domain (execution, notebook, debugging)
- Handlers abstract error parsing and response formatting
- Kernel management is isolated from tool logic

### 2. Excellent Claude Integration

Every tool includes Claude-specific guidance:

```python
return {
    'status': 'success',
    'claude_tip': "Code executed successfully. Variables are preserved.",
    'claude_next': "Use jupyter_inspect_namespace() to see defined variables"
}
```

The error handler maps Python exceptions to actionable fixes:

```python
# ModuleNotFoundError -> suggests: "uv add {package}"
# FileNotFoundError -> suggests: "Check path with os.getcwd()"
# NameError -> suggests: "Define variable before use"
```

### 3. Smart Error Handling

The `ErrorHandler` class provides:
- Package name mapping (e.g., `cv2` → `opencv-python`, `sklearn` → `scikit-learn`)
- Traceback parsing with error location extraction
- Claude-specific guidance for each error type

### 4. UV-First Philosophy

Prioritizes modern Python tooling:
- Environment detection for UV projects
- Dependency synchronization via `uv.lock`
- Package installation through UV instead of pip

### 5. Notebook Templates

Pre-built templates for common workflows:
- Data analysis
- ML experiments
- Visualization

---

## Issues Identified

### Critical Issues

#### 1. Hardcoded Heavy Dependencies

**File**: `pyproject.toml`

```toml
dependencies = [
    "fastmcp>=2.11.0",
    "jupyter",
    "ipykernel",
    "nbformat",
    "jupyter-client",
    "torch>=2.8.0",      # PROBLEM: ~2GB download
    "numpy>=2.3.2",      # PROBLEM: Unnecessary
    "matplotlib>=3.10.5", # PROBLEM: Unnecessary
]
```

**Impact**: 
- Installation size balloons from ~50MB to ~2.5GB+
- Forces specific versions that may conflict with user projects
- PyTorch triggers CUDA detection on systems without GPU

**Root Cause**: Author likely developed with ML workloads and included their working dependencies.

**Fix**:
```toml
dependencies = [
    "fastmcp>=2.11.0",
    "jupyter",
    "ipykernel",
    "nbformat",
    "jupyter-client",
]
```

#### 2. Hardcoded Kernel Name Without Fallback

**File**: `src/ml_jupyter_mcp/kernel/manager.py`

```python
self.kernel_manager = KernelManager(kernel_name='claude-jupy')
```

**Impact**: Server crashes on first run if `claude-jupy` kernelspec isn't registered.

**Fix**:
```python
def start_kernel(self) -> Dict[str, Any]:
    if self.kernel_manager and self.kernel_manager.is_alive():
        return {'status': 'already_running', ...}
    
    try:
        # Try project-specific kernel first
        for kernel_name in ['claude-jupy', 'python3']:
            try:
                self.kernel_manager = KernelManager(kernel_name=kernel_name)
                self.kernel_manager.start_kernel()
                break
            except Exception:
                continue
        else:
            raise RuntimeError("No suitable kernel found")
        
        # ... rest of initialization
```

#### 3. Global Singleton Pattern

**File**: `src/ml_jupyter_mcp/kernel/manager.py`

```python
_kernel_manager = None

def get_kernel_manager() -> SimpleKernelManager:
    global _kernel_manager
    if _kernel_manager is None:
        _kernel_manager = SimpleKernelManager()
    return _kernel_manager
```

**Impact**: Only one kernel instance can exist. No multi-session support.

**Assessment**: Acceptable for OpenCode use case (single user, single session), but should be documented.

### Moderate Issues

#### 4. Fake Session ID Parameter

**Files**: Multiple tool files

```python
def jupyter_execute_cell(session_id: str, code: str, ...) -> Dict[str, Any]:
    # session_id is never used for anything
    ...
```

**Impact**: Misleading API - users expect session isolation that doesn't exist.

**Fix Options**:
- A) Remove parameter entirely
- B) Document as "reserved for future use"
- C) Implement actual session support

#### 5. Missing Environment Modules

**File**: `src/ml_jupyter_mcp/tools/environment.py`

```python
from ..environment import UVManager, EnvironmentDetector
```

**Issue**: The `environment/` directory exists but contents weren't visible in API calls. May be incomplete.

**Impact**: UV-related tools (`jupyter_initialize`, `jupyter_detect_uv_environment`, etc.) may crash.

**Fix**: Verify module exists and is complete, or stub out UV features.

#### 6. Dead Code

**Files**:
- `src/ml_jupyter_mcp/daemon/kernel_daemon.py.old`
- Legacy tools that wrap new tools

**Impact**: Confusion, maintenance burden.

**Fix**: Remove `.old` file, consolidate or remove legacy wrappers.

#### 7. Excessive Tool Count

**Current tools**: 20+ registered tools

**Impact**: Each tool adds 200-500 tokens to context. Total: 4,000-10,000 tokens overhead.

**Fix**: Create "lite" mode with essential tools only:
- `jupyter_execute_cell`
- `jupyter_kernel_status`
- `jupyter_shutdown_kernel`
- `jupyter_create_notebook`
- `jupyter_add_cell`

### Minor Issues

#### 8. Inconsistent Error Response Format

```python
# Some functions return:
{'status': 'error', 'error': 'message'}

# Others return:
{'status': 'error', 'message': 'message'}
```

**Fix**: Standardize on `{'status': 'error', 'error': str, 'message': str}`.

#### 9. Missing Type Hints

Many functions lack proper type annotations despite Python 3.11+ requirement.

#### 10. No Unit Tests

Test files are mostly:
- Shell scripts for integration testing
- Structure validation
- No pytest unit tests for core functionality

---

## OpenCode Integration Feasibility

### Compatibility Assessment

| Requirement | ClaudeJupy Support | Notes |
|-------------|-------------------|-------|
| Local MCP server | Yes | FastMCP with stdio transport |
| Command-based startup | Yes | `python -m ml_jupyter_mcp.server` |
| Environment variables | Yes | Standard support |
| Tool registration | Yes | FastMCP auto-registers |
| Timeout support | Yes | OpenCode config works |

### Proposed Configuration

```json
{
  "mcp": {
    "jupyter": {
      "type": "local",
      "command": [
        "/path/to/venv/bin/python",
        "-m",
        "ml_jupyter_mcp.server"
      ],
      "enabled": true,
      "timeout": 30000,
      "environment": {
        "PYTHONPATH": "/path/to/ClaudeJupy/src"
      }
    }
  }
}
```

### Context Token Impact

- **Tools registered**: ~20
- **Tokens per tool**: 200-500
- **Total overhead**: 4,000-10,000 tokens per session

**Recommendation**: Use OpenCode's tool filtering:

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

## Recommended Fixes (Priority Order)

### Priority 1: Critical (Must Fix)

| # | Issue | File | Change |
|---|-------|------|--------|
| 1 | Remove heavy dependencies | `pyproject.toml` | Delete torch, numpy, matplotlib from dependencies |
| 2 | Add kernel fallback | `kernel/manager.py` | Try claude-jupy, fallback to python3 |

### Priority 2: Important (Should Fix)

| # | Issue | File | Change |
|---|-------|------|--------|
| 3 | Verify environment module | `environment/` | Ensure UVManager exists or stub |
| 4 | Clean up session_id | Multiple | Document as unused or remove |
| 5 | Remove dead code | `daemon/` | Delete `.old` file |

### Priority 3: Nice to Have

| # | Issue | File | Change |
|---|-------|------|--------|
| 6 | Reduce tool count | `tools/` | Create lite mode |
| 7 | Standardize errors | Multiple | Consistent error format |
| 8 | Add type hints | Multiple | Full typing |
| 9 | Add unit tests | `test/` | pytest for core functions |

---

## Pre-Integration Checklist

Before adding to OpenCode:

- [ ] Fork repository
- [ ] Remove torch/numpy/matplotlib from `pyproject.toml`
- [ ] Add kernel fallback to python3
- [ ] Verify environment module exists
- [ ] Install package: `uv pip install -e .`
- [ ] Register kernelspec: `python -m ipykernel install --user --name python3`
- [ ] Test server starts: `python -m ml_jupyter_mcp.server`
- [ ] Add to `opencode.json`
- [ ] Test basic execution in OpenCode

---

## Conclusion

ClaudeJupy is a well-architected project with excellent Claude-specific integrations. The error handling and guidance systems are particularly impressive. However, the critical dependency issues (PyTorch, hardcoded kernel) must be resolved before production use.

**Recommendation**: Fork, fix Priority 1 issues, then integrate with OpenCode.

**Estimated effort**: 1-2 hours for critical fixes, 4-6 hours for full cleanup.

---

## Appendix: Tool Inventory

### Execution Tools
- `execute_code` (legacy)
- `jupyter_execute_cell`
- `jupyter_execute_magic`
- `jupyter_run_file`
- `jupyter_execute_notebook`

### Environment Tools
- `jupyter_initialize`
- `jupyter_detect_uv_environment`
- `jupyter_setup_uv_environment`
- `jupyter_ensure_dependencies`
- `jupyter_sync_environment`
- `jupyter_validate_setup`

### Notebook Tools
- `add_notebook_cell` (legacy)
- `jupyter_create_notebook`
- `jupyter_add_cell`
- `jupyter_update_cell`
- `jupyter_get_notebook_info`
- `jupyter_save_notebook`

### Debugging Tools
- `jupyter_inspect_namespace`
- `jupyter_inspect_variable`
- `jupyter_list_variables`
- `jupyter_debug_last_error`
- `jupyter_profile_code`

### Guidance Tools
- `jupyter_get_guidance`
- `jupyter_what_next`

### Status Tools
- `kernel_status` (legacy)
- `shutdown_kernel` (legacy)
- `jupyter_kernel_status`
- `jupyter_shutdown_kernel`
