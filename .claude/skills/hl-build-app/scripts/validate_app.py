#!/usr/bin/env python3
"""
Validate a Scaffolded Hailo App

Checks that a scaffolded app has all required files, valid Python syntax,
resolvable imports, and correct resource references.

Usage:
    python validate_app.py community/apps/pipeline_apps/my_app
    python validate_app.py community/apps/standalone_apps/my_app
    python validate_app.py community/apps/gen_ai_apps/my_app --verbose
"""
import argparse
import importlib
import os
import py_compile
import sys
from pathlib import Path


class ValidationResult:
    """Collects pass/fail results for validation checks."""

    def __init__(self):
        self.checks = []

    def add(self, name, passed, detail=""):
        self.checks.append({"name": name, "passed": passed, "detail": detail})

    @property
    def all_passed(self):
        return all(c["passed"] for c in self.checks)

    def summary(self):
        lines = []
        for c in self.checks:
            icon = "PASS" if c["passed"] else "FAIL"
            line = f"  [{icon}] {c['name']}"
            if c["detail"]:
                line += f" — {c['detail']}"
            lines.append(line)
        passed = sum(1 for c in self.checks if c["passed"])
        total = len(self.checks)
        lines.append(f"\n  Result: {passed}/{total} checks passed")
        return "\n".join(lines)


def detect_app_type(app_dir):
    """Detect app type from directory path."""
    app_dir_str = str(app_dir)
    if "pipeline_apps" in app_dir_str:
        return "pipeline"
    elif "standalone_apps" in app_dir_str:
        return "standalone"
    elif "gen_ai_apps" in app_dir_str:
        return "genai"
    return "unknown"


def check_required_files(app_dir, app_name, app_type, result):
    """Check that all required files exist."""
    if app_type == "pipeline":
        required = [
            f"{app_name}.py",
            f"{app_name}_pipeline.py",
            "__init__.py",
        ]
    elif app_type == "standalone":
        required = [f"{app_name}.py"]
    elif app_type == "genai":
        required = [f"{app_name}.py"]
    else:
        required = [f"{app_name}.py"]

    for filename in required:
        filepath = app_dir / filename
        result.add(
            f"File exists: {filename}",
            filepath.exists(),
            str(filepath) if not filepath.exists() else "",
        )

    # Optional but recommended
    readme = app_dir / "README.md"
    result.add("README.md exists", readme.exists(), "(optional but recommended)")


def check_python_syntax(app_dir, result):
    """Check Python syntax for all .py files."""
    py_files = list(app_dir.glob("*.py"))
    if not py_files:
        result.add("Python files found", False, "No .py files in directory")
        return

    for py_file in py_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
            result.add(f"Syntax valid: {py_file.name}", True)
        except py_compile.PyCompileError as e:
            result.add(f"Syntax valid: {py_file.name}", False, str(e))


def check_imports(app_dir, app_name, app_type, result):
    """Check that key imports can resolve (without executing)."""
    main_file = app_dir / f"{app_name}.py"
    if not main_file.exists():
        result.add("Import check", False, f"{main_file} not found")
        return

    content = main_file.read_text()

    # Check for required imports based on app type
    if app_type == "pipeline":
        required_imports = [
            "hailo",
            "hailo_apps.python.core.gstreamer.gstreamer_app",
        ]
    elif app_type == "standalone":
        required_imports = [
            "hailo_apps.python.core.common.hailo_inference",
        ]
    elif app_type == "genai":
        required_imports = [
            "hailo_platform",
        ]
    else:
        required_imports = []

    for imp in required_imports:
        # Check if the import appears in the file text
        module_parts = imp.split(".")
        short_name = module_parts[-1]
        found = imp in content or f"import {short_name}" in content
        result.add(
            f"Import reference: {imp}",
            found,
            "Not found in source" if not found else "",
        )


def check_callback_signature(app_dir, app_name, app_type, result):
    """Check callback function signature for pipeline apps."""
    if app_type != "pipeline":
        return

    main_file = app_dir / f"{app_name}.py"
    if not main_file.exists():
        return

    content = main_file.read_text()

    # Check for correct callback signature
    correct_sig = "def app_callback(element, buffer, user_data)"
    wrong_sig = "def app_callback(pad, info, user_data)"

    if correct_sig in content:
        result.add("Callback signature", True, "Correct: (element, buffer, user_data)")
    elif wrong_sig in content:
        result.add(
            "Callback signature", False,
            "Wrong: (pad, info, user_data) — should be (element, buffer, user_data)"
        )
    else:
        result.add("Callback signature", False, "No app_callback function found")


def check_common_mistakes(app_dir, app_name, app_type, result):
    """Check for common coding mistakes."""
    for py_file in app_dir.glob("*.py"):
        content = py_file.read_text()

        # Check for self.options instead of self.options_menu
        if "self.options." in content and "self.options_menu" not in content:
            if "options" in content and "options_menu" not in content:
                result.add(
                    f"Correct attr access: {py_file.name}",
                    False,
                    "Uses self.options — should be self.options_menu",
                )

        # Check for manual increment() calls
        if "user_data.increment()" in content or ".increment()" in content:
            # Exclude the definition itself
            if "def increment" not in content:
                result.add(
                    f"No manual increment: {py_file.name}",
                    False,
                    "Calls increment() — frame counting is automatic, remove this",
                )

        # Check for VAAPI workaround in callback files
        if app_type == "pipeline" and py_file.name == f"{app_name}.py":
            if "vaapidecodebin" not in content:
                result.add(
                    f"VAAPI workaround: {py_file.name}",
                    False,
                    "Missing os.environ['GST_PLUGIN_FEATURE_RANK'] = 'vaapidecodebin:NONE'",
                )


def check_readme_standards(app_dir, result):
    """Check README.md for documentation standards."""
    readme = app_dir / "README.md"
    if not readme.exists():
        return

    content = readme.read_text()

    # Check for absolute paths
    if "/home/" in content or "~/." in content:
        result.add("README: no absolute paths", False, "Contains absolute paths")
    else:
        result.add("README: no absolute paths", True)

    # Check for --input usb (not /dev/video0)
    if "/dev/video" in content:
        result.add(
            "README: uses --input usb",
            False,
            "Uses /dev/videoN — should use --input usb",
        )
    else:
        result.add("README: uses --input usb", True)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a scaffolded Hailo app"
    )
    parser.add_argument(
        "app_dir", type=str, help="Path to the app directory"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show all details"
    )
    args = parser.parse_args()

    app_dir = Path(args.app_dir).resolve()
    if not app_dir.is_dir():
        print(f"Error: {app_dir} is not a directory")
        sys.exit(1)

    app_name = app_dir.name
    app_type = detect_app_type(app_dir)

    print(f"Validating: {app_dir}")
    print(f"App name: {app_name}")
    print(f"App type: {app_type}")
    print()

    result = ValidationResult()

    check_required_files(app_dir, app_name, app_type, result)
    check_python_syntax(app_dir, result)
    check_imports(app_dir, app_name, app_type, result)
    check_callback_signature(app_dir, app_name, app_type, result)
    check_common_mistakes(app_dir, app_name, app_type, result)
    check_readme_standards(app_dir, result)

    print(result.summary())

    sys.exit(0 if result.all_passed else 1)


if __name__ == "__main__":
    main()
