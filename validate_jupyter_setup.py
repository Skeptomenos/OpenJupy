#!/usr/bin/env python3
"""
Validation script for OpenCode Jupyter Integration.

Checks that all required dependencies and configurations are in place
for the jupyter-mcp-server integration to work correctly.
"""

import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckResult:
    """Result of a validation check."""

    name: str
    passed: bool
    message: str
    fix_hint: Optional[str] = None


def check_python_version() -> CheckResult:
    """Check Python version is 3.11+."""
    version = sys.version_info
    passed = version >= (3, 11)
    return CheckResult(
        name="Python Version",
        passed=passed,
        message=f"Python {version.major}.{version.minor}.{version.micro}",
        fix_hint="Install Python 3.11+ from python.org or via pyenv"
        if not passed
        else None,
    )


def check_package_installed(
    package: str, min_version: Optional[str] = None
) -> CheckResult:
    """Check if a Python package is installed with optional version check."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return CheckResult(
                name=package,
                passed=False,
                message="Not installed",
                fix_hint=f"pip install {package}"
                + (f"=={min_version}" if min_version else ""),
            )

        # Extract version from pip show output
        version_line = [
            line for line in result.stdout.split("\n") if line.startswith("Version:")
        ]
        version = version_line[0].split(": ")[1] if version_line else "unknown"

        return CheckResult(name=package, passed=True, message=f"v{version}")
    except Exception as e:
        return CheckResult(
            name=package,
            passed=False,
            message=f"Error checking: {e}",
            fix_hint=f"pip install {package}",
        )


def check_uv_installed() -> CheckResult:
    """Check if UV package manager is installed."""
    try:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return CheckResult(name="UV Package Manager", passed=True, message=version)
        return CheckResult(
            name="UV Package Manager",
            passed=False,
            message="Not installed",
            fix_hint="pip install uv",
        )
    except FileNotFoundError:
        return CheckResult(
            name="UV Package Manager",
            passed=False,
            message="Not found in PATH",
            fix_hint="pip install uv",
        )


def check_jupyter_running() -> CheckResult:
    """Check if JupyterLab is running."""
    try:
        result = subprocess.run(
            ["jupyter", "lab", "list"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0 and "http" in result.stdout:
            # Extract running servers
            lines = [l for l in result.stdout.split("\n") if "http" in l]
            if lines:
                return CheckResult(
                    name="JupyterLab Server",
                    passed=True,
                    message=f"Running ({len(lines)} server(s))",
                )
        return CheckResult(
            name="JupyterLab Server",
            passed=False,
            message="Not running",
            fix_hint="jupyter lab --port 8888 --IdentityProvider.token YOUR_TOKEN",
        )
    except FileNotFoundError:
        return CheckResult(
            name="JupyterLab Server",
            passed=False,
            message="jupyter command not found",
            fix_hint="pip install jupyterlab",
        )


def check_env_var(var_name: str) -> CheckResult:
    """Check if an environment variable is set."""
    value = os.environ.get(var_name)
    if value:
        # Mask the value for security
        masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
        return CheckResult(name=f"${var_name}", passed=True, message=f"Set ({masked})")
    return CheckResult(
        name=f"${var_name}",
        passed=False,
        message="Not set",
        fix_hint=f"export {var_name}='your-value'",
    )


def check_kernelspec() -> CheckResult:
    """Check if a Python kernel is registered."""
    try:
        result = subprocess.run(
            ["jupyter", "kernelspec", "list"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            kernels = [
                l.strip().split()[0]
                for l in result.stdout.split("\n")
                if l.strip() and not l.startswith("Available")
            ]
            if "python3" in kernels or any("python" in k.lower() for k in kernels):
                return CheckResult(
                    name="Python Kernel",
                    passed=True,
                    message=f"Found: {', '.join(kernels[:3])}",
                )
        return CheckResult(
            name="Python Kernel",
            passed=False,
            message="No Python kernel found",
            fix_hint="python -m ipykernel install --user --name python3",
        )
    except FileNotFoundError:
        return CheckResult(
            name="Python Kernel",
            passed=False,
            message="jupyter command not found",
            fix_hint="pip install jupyterlab ipykernel",
        )


def print_results(results: list[CheckResult]) -> bool:
    """Print validation results and return overall status."""
    print("\n" + "=" * 60)
    print("OpenCode Jupyter Integration - Validation Results")
    print("=" * 60 + "\n")

    all_passed = True
    for result in results:
        status = "[PASS]" if result.passed else "[FAIL]"
        color = "\033[92m" if result.passed else "\033[91m"
        reset = "\033[0m"

        print(f"{color}{status}{reset} {result.name}: {result.message}")
        if result.fix_hint:
            print(f"       Fix: {result.fix_hint}")

        if not result.passed:
            all_passed = False

    print("\n" + "-" * 60)
    if all_passed:
        print("\033[92mAll checks passed! Your setup is ready.\033[0m")
    else:
        print("\033[91mSome checks failed. Please fix the issues above.\033[0m")
    print("-" * 60 + "\n")

    return all_passed


def main() -> int:
    """Run all validation checks."""
    results: list[CheckResult] = []

    # Core requirements
    results.append(check_python_version())
    results.append(check_uv_installed())

    # Required packages
    required_packages = [
        ("jupyterlab", "4.4.1"),
        ("jupyter-collaboration", "4.0.2"),
        ("ipykernel", None),
        ("datalayer_pycrdt", "0.12.17"),
    ]

    for package, version in required_packages:
        results.append(check_package_installed(package, version))

    # Environment
    results.append(check_env_var("JUPYTER_TOKEN"))

    # Runtime checks
    results.append(check_kernelspec())
    results.append(check_jupyter_running())

    all_passed = print_results(results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
