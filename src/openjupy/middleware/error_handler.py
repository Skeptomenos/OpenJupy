"""
Error handler for parsing Python tracebacks and providing actionable fix suggestions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from openjupy.mappings.error_fixes import ERROR_FIX_MAP, FixSuggestion
from openjupy.mappings.packages import get_correct_package_name


@dataclass
class ParsedError:
    """Parsed error information from a Python traceback."""

    error_type: str
    error_message: str
    file_path: str | None = None
    line_number: int | None = None
    function_name: str | None = None
    code_context: str | None = None
    extracted_values: dict[str, str] = field(default_factory=dict)


@dataclass
class ErrorAnalysis:
    """Complete error analysis with fix suggestions."""

    parsed_error: ParsedError
    fix_suggestion: FixSuggestion | None
    claude_tip: str
    claude_next: str
    suggested_action: str | None = None


class ErrorHandler:
    """
    Handles Python tracebacks by parsing them and providing actionable fix suggestions.

    This class intercepts Jupyter execution errors and enriches them with:
    - Parsed error information (type, message, location)
    - Fix suggestions based on error type
    - Claude-specific tips and next steps
    """

    MODULE_NOT_FOUND_PATTERN = re.compile(r"No module named ['\"]?([^'\"]+)['\"]?")
    IMPORT_ERROR_PATTERN = re.compile(r"cannot import name ['\"]?([^'\"]+)['\"]?")
    NAME_ERROR_PATTERN = re.compile(r"name ['\"]?([^'\"]+)['\"]? is not defined")
    ATTRIBUTE_ERROR_PATTERN = re.compile(
        r"['\"]?([^'\"]+)['\"]? object has no attribute ['\"]?([^'\"]+)['\"]?"
    )
    KEY_ERROR_PATTERN = re.compile(r"['\"]?([^'\"]+)['\"]?")
    FILE_NOT_FOUND_PATTERN = re.compile(
        r"\[Errno 2\] No such file or directory: ['\"]?([^'\"]+)['\"]?"
    )
    TRACEBACK_LINE_PATTERN = re.compile(r'File "([^"]+)", line (\d+)(?:, in ([^\n]+))?')

    def parse_traceback(self, traceback_text: str) -> ParsedError:
        """
        Parse a Python traceback string into structured error information.

        Args:
            traceback_text: The full traceback text from Jupyter execution.

        Returns:
            ParsedError with extracted information.
        """
        lines = traceback_text.strip().split("\n")

        error_type = "UnknownError"
        error_message = ""
        file_path = None
        line_number = None
        function_name = None
        code_context = None
        extracted_values: dict[str, str] = {}

        for line in reversed(lines):
            if ": " in line and not line.startswith(" "):
                parts = line.split(": ", 1)
                error_type = parts[0].strip()
                error_message = parts[1].strip() if len(parts) > 1 else ""
                break

        for i, line in enumerate(lines):
            match = self.TRACEBACK_LINE_PATTERN.search(line)
            if match:
                file_path = match.group(1)
                line_number = int(match.group(2))
                function_name = match.group(3)
                if i + 1 < len(lines) and lines[i + 1].startswith("    "):
                    code_context = lines[i + 1].strip()

        extracted_values = self._extract_error_values(error_type, error_message)

        return ParsedError(
            error_type=error_type,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            code_context=code_context,
            extracted_values=extracted_values,
        )

    def _extract_error_values(self, error_type: str, error_message: str) -> dict[str, str]:
        """Extract relevant values from error message based on error type."""
        values: dict[str, str] = {}

        if error_type == "ModuleNotFoundError":
            match = self.MODULE_NOT_FOUND_PATTERN.search(error_message)
            if match:
                module = match.group(1)
                values["module"] = module
                values["package"] = get_correct_package_name(module)

        elif error_type == "ImportError":
            match = self.IMPORT_ERROR_PATTERN.search(error_message)
            if match:
                values["name"] = match.group(1)

        elif error_type == "NameError":
            match = self.NAME_ERROR_PATTERN.search(error_message)
            if match:
                values["name"] = match.group(1)

        elif error_type == "AttributeError":
            match = self.ATTRIBUTE_ERROR_PATTERN.search(error_message)
            if match:
                values["type"] = match.group(1)
                values["attribute"] = match.group(2)

        elif error_type == "KeyError":
            match = self.KEY_ERROR_PATTERN.search(error_message)
            if match:
                values["key"] = match.group(1)

        elif error_type == "FileNotFoundError":
            match = self.FILE_NOT_FOUND_PATTERN.search(error_message)
            if match:
                values["path"] = match.group(1)

        return values

    def analyze_error(self, traceback_text: str) -> ErrorAnalysis:
        """
        Analyze a traceback and provide complete error analysis with suggestions.

        Args:
            traceback_text: The full traceback text from Jupyter execution.

        Returns:
            ErrorAnalysis with parsed error, suggestions, and Claude guidance.
        """
        parsed = self.parse_traceback(traceback_text)
        fix_suggestion = ERROR_FIX_MAP.get(parsed.error_type)

        claude_tip = self._generate_claude_tip(parsed, fix_suggestion)
        claude_next = self._generate_claude_next(parsed, fix_suggestion)
        suggested_action = self._generate_action(parsed, fix_suggestion)

        return ErrorAnalysis(
            parsed_error=parsed,
            fix_suggestion=fix_suggestion,
            claude_tip=claude_tip,
            claude_next=claude_next,
            suggested_action=suggested_action,
        )

    def _generate_claude_tip(self, parsed: ParsedError, fix: FixSuggestion | None) -> str:
        """Generate a Claude-specific tip explaining the error."""
        if fix and fix.message_template:
            try:
                return fix.message_template.format(**parsed.extracted_values)
            except KeyError:
                pass

        location = ""
        if parsed.file_path and parsed.line_number:
            location = f" at {parsed.file_path}:{parsed.line_number}"

        return f"{parsed.error_type}{location}: {parsed.error_message}"

    def _generate_claude_next(self, parsed: ParsedError, fix: FixSuggestion | None) -> str:
        """Generate a suggestion for what Claude should do next."""
        if parsed.error_type == "ModuleNotFoundError":
            package = parsed.extracted_values.get("package", "")
            if package:
                return f"Install the missing package using: uv add {package}"
            return "Install the missing module using uv or pip."

        if parsed.error_type == "NameError":
            name = parsed.extracted_values.get("name", "")
            return f"Define '{name}' before using it, or check for typos."

        if parsed.error_type == "FileNotFoundError":
            return "Verify the file path. Use os.getcwd() to check current directory."

        if fix and fix.action_template:
            try:
                return fix.action_template.format(**parsed.extracted_values)
            except KeyError:
                return fix.action_template

        return "Review the error and fix the underlying issue."

    def _generate_action(self, parsed: ParsedError, fix: FixSuggestion | None) -> str | None:
        if parsed.error_type == "ModuleNotFoundError":
            package = parsed.extracted_values.get("package")
            if package:
                return f"uv add {package}"

        if fix and fix.action_template:
            try:
                return fix.action_template.format(**parsed.extracted_values)
            except KeyError:
                return None

        return None

    def enrich_response(self, response: dict[str, Any], traceback_text: str) -> dict[str, Any]:
        """
        Enrich a Jupyter execution response with error analysis.

        Args:
            response: The original Jupyter execution response.
            traceback_text: The traceback text from the execution.

        Returns:
            Enriched response with claude_tip, claude_next, and fix suggestions.
        """
        analysis = self.analyze_error(traceback_text)

        enriched = dict(response)
        enriched["claude_tip"] = analysis.claude_tip
        enriched["claude_next"] = analysis.claude_next

        if analysis.suggested_action:
            enriched["suggested_action"] = analysis.suggested_action

        enriched["error_details"] = {
            "type": analysis.parsed_error.error_type,
            "message": analysis.parsed_error.error_message,
            "file": analysis.parsed_error.file_path,
            "line": analysis.parsed_error.line_number,
            "function": analysis.parsed_error.function_name,
        }

        return enriched
