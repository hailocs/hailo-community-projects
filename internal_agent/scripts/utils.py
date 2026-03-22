"""Shared utilities for internal agent scripts."""

import json
import os
import subprocess
import yaml
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INTERNAL_AGENT_DIR = REPO_ROOT / "internal_agent"
DATA_DIR = INTERNAL_AGENT_DIR / "data"
TEMPLATES_DIR = INTERNAL_AGENT_DIR / "templates"
INDEX_OUTPUT = REPO_ROOT / "community" / "HAILO_PROJECT_INDEX.md"


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: dict):
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def load_registry() -> dict:
    return load_yaml(DATA_DIR / "project_registry.yaml")


def load_grades() -> dict:
    return load_yaml(DATA_DIR / "project_grades.yaml")


def github_api(endpoint: str) -> Optional[dict]:
    """Call GitHub API via gh CLI. Returns parsed JSON or None on error."""
    try:
        result = subprocess.run(
            ["gh", "api", endpoint],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def extract_github_owner_repo(url: str) -> Optional[tuple[str, str]]:
    """Extract (owner, repo) from a GitHub URL."""
    url = url.rstrip("/")
    if "github.com/" not in url:
        return None
    parts = url.split("github.com/")[1].split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None


def grade_badge_url(grade: str) -> str:
    """Generate shields.io badge URL for a grade."""
    colors = {"A": "brightgreen", "B": "blue", "C": "yellow", "D": "red"}
    color = colors.get(grade, "lightgrey")
    return f"https://img.shields.io/badge/grade-{grade}-{color}"


def stars_badge_url(owner: str, repo: str) -> str:
    return f"https://img.shields.io/github/stars/{owner}/{repo}?style=social"


def last_commit_badge_url(owner: str, repo: str) -> str:
    return f"https://img.shields.io/github/last-commit/{owner}/{repo}"


def youtube_thumbnail(video_id: str, quality: str = "hqdefault") -> str:
    """YouTube thumbnail URL. quality: default, mqdefault, hqdefault, maxresdefault."""
    return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"


def youtube_embed_html(video_id: str, width: int = 560, alt: str = "Demo") -> str:
    """HTML for embedded YouTube video thumbnail with play overlay."""
    thumb = youtube_thumbnail(video_id, "hqdefault")
    url = f"https://www.youtube.com/watch?v={video_id}"
    return (
        f'<a href="{url}">'
        f'<img src="{thumb}" width="{width}" alt="{alt}">'
        f'</a>'
    )


def extract_youtube_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    if "youtube.com/watch" in url:
        for param in url.split("?")[1].split("&"):
            if param.startswith("v="):
                return param[2:]
    if "youtube.com/shorts/" in url:
        return url.split("shorts/")[1].split("?")[0]
    return None


def compute_grade(scores: dict) -> tuple[str, float]:
    """Compute letter grade and weighted score from dimension scores."""
    weights = {
        "code_quality": 0.25,
        "community_signal": 0.20,
        "freshness": 0.20,
        "completeness": 0.20,
        "hailo_integration": 0.15,
    }
    total = sum(scores.get(dim, 0) * w for dim, w in weights.items())
    if total >= 2.5:
        letter = "A"
    elif total >= 1.8:
        letter = "B"
    elif total >= 1.0:
        letter = "C"
    else:
        letter = "D"
    return letter, round(total, 2)
