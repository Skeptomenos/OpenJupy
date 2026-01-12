"""
OpenJupy - OpenCode Jupyter Integration.

Smart error handling middleware for Jupyter notebooks that provides
actionable fix suggestions and Claude-specific guidance.
"""

from openjupy.middleware.error_handler import ErrorHandler
from openjupy.middleware.response_wrapper import ResponseWrapper

__version__ = "0.1.0"
__all__ = ["ErrorHandler", "ResponseWrapper", "__version__"]
