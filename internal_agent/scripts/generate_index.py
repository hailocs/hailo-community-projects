#!/usr/bin/env python3
"""Generate the public HAILO_PROJECT_INDEX.md from YAML data.

Reads project_registry.yaml + project_grades.yaml, applies ordering,
and renders a visually attractive markdown index with large video embeds.

Usage:
    python generate_index.py
    python generate_index.py --dry-run  # Print to stdout instead of file
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    load_yaml, DATA_DIR, INDEX_OUTPUT,
    grade_badge_url, stars_badge_url, last_commit_badge_url,
    extract_github_owner_repo, extract_youtube_id
)

SECTION_ORDER = [
    "youtube_tutorials",
    "hackathon",
    "genai",
    "smart_home",
    "detection",
    "robotics",
    "pose_seg_depth",
    "industrial",
    "automotive",
    "healthcare",
    "wildlife",
    "speech",
    "creative",
    "tools",
    "tutorials",
]

SECTION_ICONS = {
    "youtube_tutorials": "🎬",
    "hackathon": "🏆",
    "genai": "🧠",
    "smart_home": "🏠",
    "detection": "👁️",
    "robotics": "🤖",
    "pose_seg_depth": "🦴",
    "industrial": "🏭",
    "automotive": "🚗",
    "healthcare": "🏥",
    "wildlife": "🦊",
    "speech": "🎙️",
    "creative": "🎨",
    "tools": "🔧",
    "tutorials": "📚",
}

SECTION_TITLES = {
    "youtube_tutorials": ("YouTube Showcases & Tutorials", "Must-watch videos from creators and the Hailo community"),
    "hackathon": ("Hackathon Winners (2025)", "Projects from the 3rd annual Hailo Hackathon — 60 employees, 24 hours, Raspberry Pi 5 + AI HAT+"),
    "genai": ("GenAI & LLM Projects", "On-device large language models, vision-language models, image generation, and AI agents"),
    "smart_home": ("Smart Home & Surveillance", "NVR systems, Home Assistant integrations, multi-camera analytics, and privacy solutions"),
    "detection": ("Computer Vision — Detection", "Object detection, face recognition, license plate reading, and zero-shot classification"),
    "robotics": ("Robotics & Drones", "ROS2 integrations, autonomous drones, competition robots, and agricultural bots"),
    "pose_seg_depth": ("Pose, Segmentation & Depth", "Human pose estimation, semantic segmentation, and monocular depth estimation"),
    "industrial": ("Industrial & Retail", "Manufacturing inspection, conveyor sorting, retail analytics, and ruggedized controllers"),
    "automotive": ("Automotive & ADAS", "Surround perception, radar, LiDAR fusion, and driving scene understanding"),
    "healthcare": ("Healthcare & Medical", "Surgical intelligence, medical imaging, and ultrasound training"),
    "wildlife": ("Wildlife & Environment", "Wildlife detection cameras and environmental monitoring"),
    "speech": ("Speech & Audio", "Speech-to-text, voice assistants, and audio processing"),
    "creative": ("Creative & Fun", "Style transfer, games, and artistic applications"),
    "tools": ("Tools & Utilities", "Model converters, Docker images, Kubernetes plugins, and development aids"),
    "tutorials": ("Tutorials & Learning Resources", "Step-by-step guides, benchmarks, and reference designs"),
}


def video_embed(video_id: str, title: str = "Demo", width: int = 600) -> str:
    """Large clickable YouTube thumbnail with play button overlay."""
    thumb = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    url = f"https://www.youtube.com/watch?v={video_id}"
    return f"""
<div align="center">

[![{title}]({thumb})]({url})

**▶️ [Watch: {title}]({url})**

</div>
"""


def video_embed_row(videos: list[dict]) -> str:
    """Render a row of 2-3 video thumbnails side by side."""
    if not videos:
        return ""
    cells_header = []
    cells_thumb = []
    cells_link = []
    for v in videos[:3]:
        vid = v.get("id", "")
        title = v.get("title", "Demo")
        thumb = f"https://img.youtube.com/vi/{vid}/mqdefault.jpg"
        url = f"https://www.youtube.com/watch?v={vid}"
        cells_header.append(f"**{title}**")
        cells_thumb.append(f"[![{title}]({thumb})]({url})")
        cells_link.append(f"[▶️ Watch]({url})")
    sep = " | ".join(["---"] * len(videos[:3]))
    return (
        "| " + " | ".join(cells_header) + " |\n"
        "| " + sep + " |\n"
        "| " + " | ".join(cells_thumb) + " |\n"
        "| " + " | ".join(cells_link) + " |\n"
    )


def render_header() -> str:
    return f"""<!-- AGENT_METADATA
generated_from: internal_agent/data/project_registry.yaml
generated_at: {datetime.now().isoformat()}
generator: internal_agent/scripts/generate_index.py
-->

<div align="center">

# 🔥 Hailo AI Community Projects & Demos

### The ultimate collection of projects built with Hailo edge AI accelerators

[![Projects](https://img.shields.io/badge/projects-90+-blue?style=for-the-badge)](https://github.com/hailo-ai)
[![Videos](https://img.shields.io/badge/videos-30+-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/@hailo2062)
[![Hardware](https://img.shields.io/badge/Hailo--8_|_8L_|_10H_|_15-green?style=for-the-badge)](https://hailo.ai)

</div>

---

> **For humans:** Browse for inspiration, watch demos, find your next project.
> **For agents:** Parse the [YAML source](../internal_agent/data/project_registry.yaml) for structured data.

## Hardware at a Glance

| | Accelerator | Performance | Best For | Price Point |
|---|---|---|---|---|
| 🟢 | **Hailo-8** | 26 TOPS (INT8) | Full vision pipelines, multi-stream | M.2 module |
| 🔵 | **Hailo-8L** | 13 TOPS (INT8) | RPi AI Kit ($70), lower power | M.2 / AI Kit |
| 🟣 | **Hailo-10H** | 40 TOPS (INT4) | **GenAI**: LLM, VLM, Whisper, Stable Diffusion | AI HAT+ 2 ($130) |
| ⚪ | **Hailo-15** | Varies | On-camera AI-ISP, 4K analytics | Vision SoC |

---

"""


def render_toc(sections_with_projects: list) -> str:
    lines = ["## 📋 Table of Contents\n"]
    for section_id in sections_with_projects:
        icon = SECTION_ICONS.get(section_id, "")
        title = SECTION_TITLES.get(section_id, (section_id,))[0]
        anchor = title.lower().replace(" ", "-").replace("—", "").replace("&", "").replace("(", "").replace(")", "").replace(",", "").replace(":", "").strip().replace("  ", "-")
        lines.append(f"- [{icon} {title}](#{anchor})")
    lines.append("\n---\n")
    return "\n".join(lines)


def render_youtube_tutorials(tutorials: list) -> str:
    """Special rendering for the YouTube tutorials section — big visual grid."""
    lines = []
    for t in tutorials:
        name = t["name"]
        desc = t.get("description", "")
        channel = t.get("channel", "")
        video_urls = t.get("video_urls", [])
        hardware = t.get("hardware", [])
        hw_str = ", ".join(hardware) if isinstance(hardware, list) else hardware

        vid = None
        for vurl in video_urls:
            vid = extract_youtube_id(vurl)
            if vid:
                break

        if vid:
            lines.append(f"### {name}")
            if channel:
                lines.append(f"**Channel:** {channel} · **Hardware:** {hw_str}\n")
            lines.append(f"> {desc}\n")
            lines.append(video_embed(vid, name))
            lines.append("---\n")
    return "\n".join(lines)


def render_project_card(project: dict, grade_info: dict | None) -> str:
    """Render a single project as a visual card."""
    lines = []
    name = project["name"]
    desc = project.get("description", "")
    hardware = project.get("hardware", "")
    github_url = project.get("github_url", "")
    video_urls = project.get("video_urls", [])
    official_url = project.get("official_demo_url", "")
    features = project.get("features", [])
    status = project.get("status", "")
    partner = project.get("partner", "")

    # Title
    lines.append(f"### {name}")

    # Badges line
    badges = []
    if grade_info:
        grade = grade_info.get("grade", "")
        if grade:
            badges.append(f"![Grade: {grade}]({grade_badge_url(grade)})")

    gh_parts = extract_github_owner_repo(github_url) if github_url else None
    if gh_parts and "/tree/" not in github_url:
        owner, repo = gh_parts
        badges.append(f"[![Stars]({stars_badge_url(owner, repo)})]({github_url})")
        badges.append(f"![Last Commit]({last_commit_badge_url(owner, repo)})")

    if status:
        color = "brightgreen" if status == "production" else "blue"
        badges.append(f"![Status](https://img.shields.io/badge/status-{status}-{color})")

    if badges:
        lines.append(" ".join(badges))
    lines.append("")

    # Description as blockquote
    if desc:
        lines.append(f"> {desc}")
        lines.append("")

    # Metadata table
    meta_rows = []
    if hardware:
        hw = hardware if isinstance(hardware, str) else ", ".join(hardware)
        meta_rows.append(f"| **Hardware** | {hw} |")
    if github_url:
        short = github_url.replace("https://github.com/", "")
        meta_rows.append(f"| **GitHub** | [{short}]({github_url}) |")
    if official_url:
        meta_rows.append(f"| **Official Demo** | [hailo.ai]({official_url}) |")
    if partner:
        meta_rows.append(f"| **Partner** | {partner} |")
    if features:
        feat_str = features if isinstance(features, str) else ", ".join(features)
        meta_rows.append(f"| **Key Features** | {feat_str} |")

    if meta_rows:
        lines.append("| | |")
        lines.append("|---|---|")
        lines.extend(meta_rows)
        lines.append("")

    # Video embed — large and centered
    for vurl in video_urls:
        vid = extract_youtube_id(vurl)
        if vid:
            lines.append(video_embed(vid, name))
            break  # Only first video

    lines.append("---\n")
    return "\n".join(lines)


def generate(dry_run: bool = False):
    registry = load_yaml(DATA_DIR / "project_registry.yaml")
    grades_data = load_yaml(DATA_DIR / "project_grades.yaml")

    # Build grades lookup
    grades_by_id = {}
    for g in grades_data.get("projects", []):
        grades_by_id[g["id"]] = g

    # Group projects by section
    sections = {}
    for project in registry.get("projects", []):
        section = project.get("section", "tools")
        pid = project.get("id", "")

        # Skip D-grade projects
        grade_info = grades_by_id.get(pid)
        if grade_info and grade_info.get("grade") == "D":
            continue

        sections.setdefault(section, []).append(project)

    # Sort within each section: grade (A first), then stars
    grade_order = {"A": 0, "B": 1, "C": 2, "D": 3}
    for section_id, projects in sections.items():
        projects.sort(key=lambda p: (
            grade_order.get(grades_by_id.get(p.get("id", ""), {}).get("grade", "C"), 2),
            -(p.get("stars", 0) or 0)
        ))

    # Render
    output = []
    output.append(render_header())

    active_sections = [s for s in SECTION_ORDER if s in sections]
    output.append(render_toc(active_sections))

    for section_id in active_sections:
        projects = sections[section_id]
        title_info = SECTION_TITLES.get(section_id, (section_id, ""))
        title, subtitle = title_info
        icon = SECTION_ICONS.get(section_id, "")

        output.append(f"## {icon} {title}\n")
        if subtitle:
            output.append(f"*{subtitle}*\n")

        # Special rendering for YouTube tutorials section
        if section_id == "youtube_tutorials":
            output.append(render_youtube_tutorials(projects))
        else:
            for project in projects:
                grade_info = grades_by_id.get(project.get("id", ""))
                output.append(render_project_card(project, grade_info))

    # Footer
    output.append("""
---

<div align="center">

**[Hailo GitHub](https://github.com/hailo-ai)** · **[Hailo YouTube](https://www.youtube.com/@hailo2062)** · **[Hailo Resources](https://hailo.ai/resources/)** · **[Hailo Community](https://community.hailo.ai)**

*Auto-generated from [`project_registry.yaml`](../internal_agent/data/project_registry.yaml) by [`generate_index.py`](../internal_agent/scripts/generate_index.py)*

</div>
""")

    content = "\n".join(output)

    if dry_run:
        print(content)
    else:
        INDEX_OUTPUT.write_text(content)
        print(f"Generated {INDEX_OUTPUT} ({len(content)} bytes)")


def main():
    parser = argparse.ArgumentParser(description="Generate project index from YAML")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout")
    args = parser.parse_args()
    generate(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
