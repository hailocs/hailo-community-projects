#!/usr/bin/env python3
"""
Auto-Generate README for a Hailo App

Parses the app's Python files to extract docstrings, CLI arguments,
model information, and generates a markdown README.

Usage:
    python generate_readme.py community/apps/pipeline_apps/my_app
    python generate_readme.py community/apps/standalone_apps/my_app --output README.md
    python generate_readme.py community/apps/pipeline_apps/my_app --dry-run
"""
import argparse
import ast
import re
import sys
from pathlib import Path


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


def extract_docstring(filepath):
    """Extract module-level docstring from a Python file."""
    try:
        source = filepath.read_text()
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree)
        return docstring or ""
    except (SyntaxError, UnicodeDecodeError):
        return ""


def extract_argparse_args(filepath):
    """Extract argparse argument definitions from source code."""
    try:
        source = filepath.read_text()
    except (OSError, UnicodeDecodeError):
        return []

    args = []
    # Pattern: parser.add_argument("--name", ...)
    pattern = re.compile(
        r'parser\.add_argument\(\s*["\'](-[-\w]+)["\']'
        r'(?:.*?help\s*=\s*["\']([^"\']+)["\'])?'
        r'(?:.*?default\s*=\s*([^,\)]+))?'
        r'(?:.*?type\s*=\s*(\w+))?',
        re.DOTALL,
    )

    for match in pattern.finditer(source):
        arg_name = match.group(1)
        help_text = match.group(2) or ""
        default = match.group(3) or ""
        arg_type = match.group(4) or "str"

        # Skip standard pipeline args
        if arg_name in ("--input", "--hef-path", "--arch", "--show-fps",
                        "--use-frame", "--disable-sync", "--batch-size",
                        "--width", "--height", "--frame-rate", "--list-models"):
            continue

        args.append({
            "name": arg_name,
            "help": help_text.strip(),
            "default": default.strip().rstrip(","),
            "type": arg_type.strip(),
        })

    return args


def extract_model_info(filepath):
    """Extract model-related information from source code."""
    try:
        source = filepath.read_text()
    except (OSError, UnicodeDecodeError):
        return {}

    info = {}

    # Look for HEF-related strings
    hef_match = re.search(r'app_name\s*=\s*["\'](\w+)["\']', source)
    if hef_match:
        info["app_name"] = hef_match.group(1)

    # Look for postprocess .so
    so_match = re.search(r'["\'](\w+_postprocess\.so)["\']', source)
    if so_match:
        info["postprocess_so"] = so_match.group(1)

    # Look for postprocess function
    func_match = re.search(r'post_function_name\s*=\s*["\'](\w+)["\']', source)
    if func_match:
        info["postprocess_func"] = func_match.group(1)

    return info


def generate_readme(app_dir, app_name, app_type):
    """Generate README content for the app."""
    lines = []

    # Title
    display_name = app_name.replace("_", " ").title()
    lines.append(f"# {display_name}")
    lines.append("")

    # Description from docstring
    main_file = app_dir / f"{app_name}.py"
    docstring = extract_docstring(main_file) if main_file.exists() else ""
    if docstring:
        # Use first paragraph as description
        paragraphs = docstring.strip().split("\n\n")
        lines.append(paragraphs[0].strip())
    else:
        lines.append(f"A Hailo {app_type} app.")
    lines.append("")

    # Prerequisites
    lines.append("## Prerequisites")
    lines.append("")
    lines.append("- Hailo accelerator (Hailo-8, Hailo-8L, or Hailo-10H)")
    lines.append("- hailo-apps framework installed")
    lines.append("- Environment activated: `source setup_env.sh`")
    if app_type == "genai":
        lines.append("- Hailo-10H hardware (GenAI SDK required)")
    lines.append("")

    # Model info
    model_info = {}
    if app_type == "pipeline":
        pipeline_file = app_dir / f"{app_name}_pipeline.py"
        if pipeline_file.exists():
            model_info = extract_model_info(pipeline_file)
    else:
        if main_file.exists():
            model_info = extract_model_info(main_file)

    if model_info:
        lines.append("## Models")
        lines.append("")
        if "app_name" in model_info:
            lines.append(f"- **App config:** `{model_info['app_name']}` (from resources_config.yaml)")
        if "postprocess_so" in model_info:
            lines.append(f"- **Postprocess:** `{model_info['postprocess_so']}`")
        if "postprocess_func" in model_info:
            lines.append(f"- **Function:** `{model_info['postprocess_func']}`")
        lines.append("")

    # Usage
    lines.append("## Usage")
    lines.append("")
    lines.append("```bash")
    lines.append("# Activate environment")
    lines.append("source setup_env.sh")
    lines.append("")

    if app_type == "pipeline":
        app_path = f"community/apps/pipeline_apps/{app_name}/{app_name}.py"
        lines.append(f"# Run with default video input")
        lines.append(f"python {app_path}")
        lines.append("")
        lines.append(f"# Run with USB camera")
        lines.append(f"python {app_path} --input usb")
        lines.append("")
        lines.append(f"# Run with video file")
        lines.append(f"python {app_path} --input path/to/video.mp4")
        lines.append("")
        lines.append(f"# Show FPS and use custom frame drawing")
        lines.append(f"python {app_path} --input usb --show-fps --use-frame")
    elif app_type == "standalone":
        app_path = f"community/apps/standalone_apps/{app_name}/{app_name}.py"
        lines.append(f"# Run with video file")
        lines.append(f"python {app_path} --input video.mp4")
        lines.append("")
        lines.append(f"# Run with USB camera")
        lines.append(f"python {app_path} --input usb --show-fps")
        lines.append("")
        lines.append(f"# Save output")
        lines.append(f"python {app_path} --input images/ --save-output --output-dir results/")
    elif app_type == "genai":
        app_path = f"community/apps/gen_ai_apps/{app_name}/{app_name}.py"
        lines.append(f"# Run the app")
        lines.append(f"python {app_path}")

    lines.append("```")
    lines.append("")

    # Custom CLI args
    custom_args = extract_argparse_args(main_file)
    if app_type == "pipeline":
        pipeline_file = app_dir / f"{app_name}_pipeline.py"
        if pipeline_file.exists():
            custom_args.extend(extract_argparse_args(pipeline_file))

    if custom_args:
        lines.append("## Custom Arguments")
        lines.append("")
        lines.append("| Argument | Type | Default | Description |")
        lines.append("|----------|------|---------|-------------|")
        for a in custom_args:
            lines.append(f"| `{a['name']}` | {a['type']} | {a['default']} | {a['help']} |")
        lines.append("")

    # Architecture
    if app_type == "pipeline":
        lines.append("## Architecture")
        lines.append("")
        lines.append("```")
        lines.append("Source -> Inference -> Tracker -> Callback -> Display")
        lines.append("```")
        lines.append("")
        lines.append("This app uses the standard pipeline pattern with:")
        lines.append("- `INFERENCE_PIPELINE_WRAPPER` for resolution preservation")
        lines.append("- `TRACKER_PIPELINE` for object tracking")
        lines.append("- `USER_CALLBACK_PIPELINE` for custom processing")
        lines.append("")

    # Customization
    lines.append("## Customization")
    lines.append("")
    lines.append("- **Swap models:** Use `--hef-path <model_name>` or `--list-models`")
    if app_type == "pipeline":
        lines.append("- **Change display:** Modify `get_pipeline_string()` in the pipeline file")
        lines.append("- **Add processing:** Edit the `app_callback` function in the main file")
    elif app_type == "standalone":
        lines.append("- **Change postprocess:** Edit `inference_result_handler` in the postprocess file")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate README for a Hailo app"
    )
    parser.add_argument("app_dir", type=str, help="Path to the app directory")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output file path (default: <app_dir>/README.md)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print README to stdout without writing file")
    args = parser.parse_args()

    app_dir = Path(args.app_dir).resolve()
    if not app_dir.is_dir():
        print(f"Error: {app_dir} is not a directory")
        sys.exit(1)

    app_name = app_dir.name
    app_type = detect_app_type(app_dir)

    readme_content = generate_readme(app_dir, app_name, app_type)

    if args.dry_run:
        print(readme_content)
    else:
        output_path = Path(args.output) if args.output else app_dir / "README.md"
        output_path.write_text(readme_content)
        print(f"README written to: {output_path}")


if __name__ == "__main__":
    main()
