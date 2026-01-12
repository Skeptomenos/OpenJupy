"""
Package name mappings for common import-to-pip-package mismatches.

Many Python packages have different import names than their pip package names.
This module provides mappings to help users install the correct package.
"""

from __future__ import annotations

PACKAGE_NAME_MAP: dict[str, str] = {
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "PIL": "pillow",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "jwt": "pyjwt",
    "magic": "python-magic",
    "serial": "pyserial",
    "usb": "pyusb",
    "wx": "wxpython",
    "gi": "pygobject",
    "cairo": "pycairo",
    "Crypto": "pycryptodome",
    "OpenSSL": "pyopenssl",
    "MySQLdb": "mysqlclient",
    "psycopg2": "psycopg2-binary",
    "lxml": "lxml",
    "skimage": "scikit-image",
    "tensorflow": "tensorflow",
    "tf": "tensorflow",
    "torch": "torch",
    "torchvision": "torchvision",
    "transformers": "transformers",
    "langchain": "langchain",
    "openai": "openai",
    "anthropic": "anthropic",
    "httpx": "httpx",
    "aiohttp": "aiohttp",
    "fastapi": "fastapi",
    "flask": "flask",
    "django": "django",
    "sqlalchemy": "sqlalchemy",
    "alembic": "alembic",
    "celery": "celery",
    "redis": "redis",
    "boto3": "boto3",
    "botocore": "botocore",
    "google.cloud": "google-cloud-core",
    "azure": "azure-core",
}


def get_correct_package_name(import_name: str) -> str:
    """
    Get the correct pip package name for a given import name.

    Args:
        import_name: The module name used in the import statement.

    Returns:
        The correct pip package name, or the import name if no mapping exists.
    """
    base_module = import_name.split(".")[0]
    return PACKAGE_NAME_MAP.get(base_module, import_name)
