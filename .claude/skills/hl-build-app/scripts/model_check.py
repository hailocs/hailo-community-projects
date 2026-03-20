#!/usr/bin/env python3
"""
Verify Model Availability for a Hailo App

Checks whether a given model name has a HEF file available for the
target architecture, and whether the associated postprocess .so exists.

Usage:
    python model_check.py yolov8m hailo8
    python model_check.py scrfd_10g hailo8l
    python model_check.py Qwen2.5-1.5B-Instruct hailo10h
    python model_check.py --list           # List all known models
    python model_check.py --list --arch hailo8l  # List models for architecture
"""
import argparse
import sys
from pathlib import Path

import yaml


def find_skill_dir():
    """Find the app-builder skill directory."""
    # Try relative to this script
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    if (skill_dir / "knowledge" / "model_compatibility.yaml").exists():
        return skill_dir
    # Try from CWD
    cwd = Path.cwd()
    for candidate in [
        cwd / ".claude" / "skills" / "app-builder",
        cwd.parent / ".claude" / "skills" / "app-builder",
    ]:
        if (candidate / "knowledge" / "model_compatibility.yaml").exists():
            return candidate
    return None


def load_model_db(skill_dir):
    """Load the model compatibility database."""
    yaml_path = skill_dir / "knowledge" / "model_compatibility.yaml"
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("models", [])


def check_model(models, model_name, arch):
    """Check model availability for a given architecture."""
    # Find the model entry
    model = None
    for m in models:
        if m["name"].lower() == model_name.lower():
            model = m
            break

    if model is None:
        print(f"Model '{model_name}' not found in model_compatibility.yaml")
        print(f"Use --list to see all known models.")
        return False

    print(f"Model: {model['name']}")
    print(f"Task: {model['task']}")
    print(f"Output type: {model.get('output_type', 'N/A')}")
    print()

    # Check HEF availability
    hef_info = model.get("hef", {})
    hef_file = hef_info.get(arch)

    if hef_file:
        print(f"  [{arch}] HEF: {hef_file} — AVAILABLE")
    else:
        print(f"  [{arch}] HEF: N/A — NOT AVAILABLE for this architecture")

    # Show all architectures
    print()
    print("  Architecture support:")
    for a in ["hailo8", "hailo8l", "hailo10h"]:
        h = hef_info.get(a)
        status = h if h else "N/A"
        marker = "<--" if a == arch else ""
        print(f"    {a}: {status} {marker}")

    # Check postprocess
    print()
    pp_so = model.get("postprocess_so")
    pp_func = model.get("postprocess_func")
    if pp_so:
        print(f"  Postprocess .so: {pp_so}")
        print(f"  Postprocess func: {pp_func}")
    else:
        print(f"  Postprocess: CPU-based (no .so needed)")

    # Show labels
    labels = model.get("labels")
    if labels:
        print(f"  Labels: {labels}")

    # Show input shape
    input_shape = model.get("input_shape")
    if input_shape:
        print(f"  Input shape: {input_shape}")

    # Show which apps use this model
    used_by = model.get("used_by", [])
    if used_by:
        print(f"  Used by: {', '.join(used_by)}")

    # Notes
    notes = model.get("notes")
    if notes:
        print(f"  Notes: {notes}")

    return hef_file is not None


def list_models(models, arch=None):
    """List all known models, optionally filtered by architecture."""
    print(f"{'Model':<35} {'Task':<25} {'hailo8':<10} {'hailo8l':<10} {'hailo10h':<10}")
    print("-" * 90)

    for m in models:
        hef = m.get("hef", {})
        h8 = "Y" if hef.get("hailo8") else "-"
        h8l = "Y" if hef.get("hailo8l") else "-"
        h10h = "Y" if hef.get("hailo10h") else "-"

        # Filter by arch if specified
        if arch and not hef.get(arch):
            continue

        print(f"{m['name']:<35} {m['task']:<25} {h8:<10} {h8l:<10} {h10h:<10}")


def main():
    parser = argparse.ArgumentParser(
        description="Check model availability for Hailo apps"
    )
    parser.add_argument("model", nargs="?", help="Model name to check")
    parser.add_argument("arch", nargs="?", default="hailo8",
                        choices=["hailo8", "hailo8l", "hailo10h"],
                        help="Target architecture (default: hailo8)")
    parser.add_argument("--list", action="store_true",
                        help="List all known models")
    args = parser.parse_args()

    skill_dir = find_skill_dir()
    if skill_dir is None:
        print("Error: Cannot find model_compatibility.yaml")
        print("Run this script from the repo root or the app-builder skill directory.")
        sys.exit(1)

    models = load_model_db(skill_dir)

    if args.list:
        list_models(models, args.arch if args.model is None else None)
        sys.exit(0)

    if args.model is None:
        parser.print_help()
        sys.exit(1)

    available = check_model(models, args.model, args.arch)
    sys.exit(0 if available else 1)


if __name__ == "__main__":
    main()
