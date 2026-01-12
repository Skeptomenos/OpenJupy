"""
Package name mappings and error fix suggestions.
"""

from openjupy.mappings.error_fixes import ERROR_FIX_MAP, get_fix_suggestion
from openjupy.mappings.packages import PACKAGE_NAME_MAP, get_correct_package_name

__all__ = [
    "PACKAGE_NAME_MAP",
    "get_correct_package_name",
    "ERROR_FIX_MAP",
    "get_fix_suggestion",
]
