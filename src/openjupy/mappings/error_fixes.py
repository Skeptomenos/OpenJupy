"""
Error type to fix suggestion mappings.

Maps Python exception types to actionable fix suggestions that help
users resolve common errors quickly.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FixSuggestion:
    """A fix suggestion with a message template and optional action."""

    message_template: str
    action_template: str | None = None


ERROR_FIX_MAP: dict[str, FixSuggestion] = {
    "ModuleNotFoundError": FixSuggestion(
        message_template="Module '{module}' is not installed.",
        action_template="uv add {package}",
    ),
    "ImportError": FixSuggestion(
        message_template="Cannot import '{name}' from '{module}'.",
        action_template="Check if the module is installed correctly: uv add {package}",
    ),
    "FileNotFoundError": FixSuggestion(
        message_template="File or directory not found: '{path}'.",
        action_template="Verify the path exists. Current directory: use os.getcwd() to check.",
    ),
    "PermissionError": FixSuggestion(
        message_template="Permission denied: '{path}'.",
        action_template="Check file permissions or run with appropriate privileges.",
    ),
    "NameError": FixSuggestion(
        message_template="Name '{name}' is not defined.",
        action_template="Define the variable before use, or check for typos.",
    ),
    "AttributeError": FixSuggestion(
        message_template="'{type}' object has no attribute '{attribute}'.",
        action_template="Check the object type and available attributes using dir().",
    ),
    "TypeError": FixSuggestion(
        message_template="Type error in operation.",
        action_template="Check argument types. Use type() to inspect values.",
    ),
    "ValueError": FixSuggestion(
        message_template="Invalid value provided.",
        action_template="Check the expected value format or range.",
    ),
    "KeyError": FixSuggestion(
        message_template="Key '{key}' not found in dictionary.",
        action_template="Use .get(key, default) for safe access, or check available keys.",
    ),
    "IndexError": FixSuggestion(
        message_template="Index out of range.",
        action_template="Check sequence length with len() before accessing.",
    ),
    "ZeroDivisionError": FixSuggestion(
        message_template="Division by zero.",
        action_template="Add a check for zero before dividing.",
    ),
    "SyntaxError": FixSuggestion(
        message_template="Syntax error in code.",
        action_template="Check for missing colons, parentheses, or quotes.",
    ),
    "IndentationError": FixSuggestion(
        message_template="Indentation error.",
        action_template="Use consistent indentation (4 spaces recommended).",
    ),
    "ConnectionError": FixSuggestion(
        message_template="Connection failed.",
        action_template="Check network connectivity and the target URL/host.",
    ),
    "TimeoutError": FixSuggestion(
        message_template="Operation timed out.",
        action_template="Increase timeout or check if the service is responding.",
    ),
    "MemoryError": FixSuggestion(
        message_template="Out of memory.",
        action_template="Reduce data size, use generators, or process in chunks.",
    ),
    "RecursionError": FixSuggestion(
        message_template="Maximum recursion depth exceeded.",
        action_template="Add a base case or convert to iterative approach.",
    ),
}


def get_fix_suggestion(
    error_type: str,
    _error_message: str,
    _context: dict[str, str] | None = None,
) -> FixSuggestion | None:
    return ERROR_FIX_MAP.get(error_type)
