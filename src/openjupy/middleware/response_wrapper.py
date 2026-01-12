"""
Response wrapper for enriching Jupyter tool responses with Claude guidance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openjupy.middleware.error_handler import ErrorHandler


@dataclass
class NamespaceInfo:
    """Information about the current Jupyter namespace."""

    variables: list[str]
    dataframes: list[str]
    functions: list[str]
    classes: list[str]


class ResponseWrapper:
    """
    Wraps Jupyter tool responses with Claude-specific guidance.

    Adds claude_tip and claude_next fields to help Claude understand
    the execution context and suggest appropriate next steps.
    """

    def __init__(self) -> None:
        self.error_handler = ErrorHandler()

    def wrap_execution_success(
        self,
        response: dict[str, Any],
        output: str | None = None,
        namespace_vars: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Wrap a successful execution response with guidance.

        Args:
            response: The original execution response.
            output: The execution output (if any).
            namespace_vars: List of variable names in the namespace.

        Returns:
            Enriched response with claude_tip and claude_next.
        """
        enriched = dict(response)
        enriched["status"] = "success"

        tips: list[str] = []
        next_steps: list[str] = []

        if output:
            tips.append("Code executed successfully with output.")
        else:
            tips.append("Code executed successfully (no output).")

        if namespace_vars:
            df_vars = [v for v in namespace_vars if v.endswith("_df") or v == "df"]
            if df_vars:
                tips.append(f"DataFrames available: {', '.join(df_vars)}")
                next_steps.append(
                    f"Explore data with {df_vars[0]}.head() or {df_vars[0]}.describe()"
                )

            if len(namespace_vars) > 0:
                tips.append(f"Namespace contains {len(namespace_vars)} variable(s).")
                next_steps.append("Use jupyter_inspect_namespace() to see all defined variables.")

        enriched["claude_tip"] = " ".join(tips) if tips else "Execution complete."
        enriched["claude_next"] = (
            " ".join(next_steps) if next_steps else "Continue with your analysis."
        )

        return enriched

    def wrap_execution_error(
        self,
        response: dict[str, Any],
        traceback_text: str,
    ) -> dict[str, Any]:
        """
        Wrap an error execution response with fix suggestions.

        Args:
            response: The original execution response.
            traceback_text: The full traceback text.

        Returns:
            Enriched response with error analysis and fix suggestions.
        """
        enriched = dict(response)
        enriched["status"] = "error"

        return self.error_handler.enrich_response(enriched, traceback_text)

    def wrap_notebook_created(
        self,
        response: dict[str, Any],
        notebook_path: str,
        kernel_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Wrap a notebook creation response with guidance.

        Args:
            response: The original response.
            notebook_path: Path to the created notebook.
            kernel_name: Name of the kernel (if specified).

        Returns:
            Enriched response with next steps.
        """
        enriched = dict(response)
        enriched["status"] = "success"
        enriched["claude_tip"] = f"Notebook created at {notebook_path}."

        if kernel_name:
            enriched["claude_tip"] += f" Using kernel: {kernel_name}."

        enriched["claude_next"] = (
            "Add cells with jupyter_add_cell() or execute code with jupyter_execute_cell()."
        )

        return enriched

    def wrap_cell_added(
        self,
        response: dict[str, Any],
        cell_type: str,
        cell_index: int,
    ) -> dict[str, Any]:
        """
        Wrap a cell addition response with guidance.

        Args:
            response: The original response.
            cell_type: Type of cell added (code/markdown).
            cell_index: Index of the new cell.

        Returns:
            Enriched response with next steps.
        """
        enriched = dict(response)
        enriched["status"] = "success"
        enriched["claude_tip"] = f"{cell_type.capitalize()} cell added at index {cell_index}."

        if cell_type == "code":
            enriched["claude_next"] = "Execute the cell with jupyter_execute_cell()."
        else:
            enriched["claude_next"] = "Add more cells or execute existing code cells."

        return enriched

    def wrap_kernel_status(
        self,
        response: dict[str, Any],
        is_alive: bool,
        execution_count: int | None = None,
    ) -> dict[str, Any]:
        """
        Wrap a kernel status response with guidance.

        Args:
            response: The original response.
            is_alive: Whether the kernel is running.
            execution_count: Number of executions (if available).

        Returns:
            Enriched response with status info.
        """
        enriched = dict(response)

        if is_alive:
            enriched["status"] = "running"
            enriched["claude_tip"] = "Kernel is running and ready for execution."
            if execution_count is not None:
                enriched["claude_tip"] += f" Execution count: {execution_count}."
            enriched["claude_next"] = "Execute code with jupyter_execute_cell()."
        else:
            enriched["status"] = "stopped"
            enriched["claude_tip"] = "Kernel is not running."
            enriched["claude_next"] = "Start the kernel or create a new notebook."

        return enriched

    def wrap_generic_success(
        self,
        response: dict[str, Any],
        operation: str,
        details: str | None = None,
    ) -> dict[str, Any]:
        """
        Wrap a generic successful operation with guidance.

        Args:
            response: The original response.
            operation: Description of the operation performed.
            details: Additional details (optional).

        Returns:
            Enriched response.
        """
        enriched = dict(response)
        enriched["status"] = "success"
        enriched["claude_tip"] = f"{operation} completed successfully."

        if details:
            enriched["claude_tip"] += f" {details}"

        enriched["claude_next"] = "Continue with your workflow."

        return enriched
