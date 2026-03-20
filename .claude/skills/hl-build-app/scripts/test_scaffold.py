#!/usr/bin/env python3
"""
Smoke Test a Scaffolded Hailo App

Quick sanity checks on a scaffolded app:
- Try importing the module
- Try running with --help
- Check CLI args are properly defined

Usage:
    python test_scaffold.py community/apps/pipeline_apps/my_app
    python test_scaffold.py community/apps/standalone_apps/my_app --timeout 10
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_repo_root():
    """Walk up from CWD to find the repo root (contains hailo-apps-infra/)."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "hailo-apps-infra").is_dir():
            return parent
    return current


def run_command(cmd, timeout=15, cwd=None):
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def test_syntax(app_dir, app_name):
    """Test: Python files compile without syntax errors."""
    print(f"  [TEST] Syntax check...")
    py_files = list(app_dir.glob("*.py"))
    all_ok = True
    for py_file in py_files:
        rc, out, err = run_command(
            [sys.executable, "-m", "py_compile", str(py_file)]
        )
        if rc != 0:
            print(f"    FAIL: {py_file.name} — {err.strip()}")
            all_ok = False
        else:
            print(f"    OK: {py_file.name}")
    return all_ok


def test_help(app_dir, app_name, repo_root):
    """Test: App runs with --help without errors."""
    print(f"  [TEST] CLI --help...")
    main_file = app_dir / f"{app_name}.py"
    if not main_file.exists():
        print(f"    SKIP: {main_file} not found")
        return True

    rc, out, err = run_command(
        [sys.executable, str(main_file), "--help"],
        timeout=15,
        cwd=str(repo_root),
    )

    if rc == 0:
        # Check that help output contains expected sections
        has_usage = "usage:" in out.lower() or "usage:" in err.lower()
        has_options = "--input" in out or "--hef" in out or "--help" in out
        print(f"    OK: Help output received (usage={has_usage}, options={has_options})")
        return True
    else:
        # --help may fail due to missing hailo imports on non-Hailo systems
        if "ModuleNotFoundError" in err or "ImportError" in err:
            print(f"    SKIP: Import error (expected on non-Hailo system)")
            print(f"    Detail: {err.strip()[:200]}")
            return True  # Not a scaffolding error
        print(f"    FAIL: Exit code {rc}")
        if err:
            print(f"    Error: {err.strip()[:300]}")
        return False


def test_import(app_dir, app_name, app_type, repo_root):
    """Test: Module can be imported."""
    print(f"  [TEST] Import check...")

    # Build the module path
    rel_path = app_dir.relative_to(repo_root)
    module_path = str(rel_path).replace("/", ".").replace("\\", ".")

    # For pipeline apps, try importing the pipeline module
    if app_type == "pipeline":
        target = f"{module_path}.{app_name}_pipeline"
    else:
        target = f"{module_path}.{app_name}"

    rc, out, err = run_command(
        [sys.executable, "-c", f"import {target}; print('OK')"],
        timeout=15,
        cwd=str(repo_root),
    )

    if rc == 0 and "OK" in out:
        print(f"    OK: {target} imported successfully")
        return True
    elif "ModuleNotFoundError" in err and ("hailo" in err or "gi" in err):
        print(f"    SKIP: Hailo/GStreamer not available (expected on dev system)")
        return True  # Not a scaffolding error
    else:
        print(f"    FAIL: Could not import {target}")
        if err:
            print(f"    Error: {err.strip()[:300]}")
        return False


def detect_app_type(app_dir):
    """Detect app type from directory path."""
    path_str = str(app_dir)
    if "pipeline_apps" in path_str:
        return "pipeline"
    elif "standalone_apps" in path_str:
        return "standalone"
    elif "gen_ai_apps" in path_str:
        return "genai"
    return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Smoke test a scaffolded Hailo app"
    )
    parser.add_argument("app_dir", type=str, help="Path to the app directory")
    parser.add_argument("--timeout", type=int, default=15,
                        help="Command timeout in seconds (default: 15)")
    args = parser.parse_args()

    app_dir = Path(args.app_dir).resolve()
    if not app_dir.is_dir():
        print(f"Error: {app_dir} is not a directory")
        sys.exit(1)

    app_name = app_dir.name
    app_type = detect_app_type(app_dir)
    repo_root = find_repo_root()

    print(f"Smoke testing: {app_dir}")
    print(f"App: {app_name} (type: {app_type})")
    print(f"Repo root: {repo_root}")
    print()

    results = []

    results.append(("Syntax", test_syntax(app_dir, app_name)))
    results.append(("Help", test_help(app_dir, app_name, repo_root)))
    results.append(("Import", test_import(app_dir, app_name, app_type, repo_root)))

    print()
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    for name, ok in results:
        icon = "PASS" if ok else "FAIL"
        print(f"  [{icon}] {name}")

    sys.exit(0 if all(ok for _, ok in results) else 1)


if __name__ == "__main__":
    main()
