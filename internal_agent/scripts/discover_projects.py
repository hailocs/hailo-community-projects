#!/usr/bin/env python3
"""Discover new Hailo-related projects on GitHub not yet in the registry.

Usage:
    python discover_projects.py
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_yaml, DATA_DIR

SEARCH_QUERIES = [
    "hailo raspberry pi",
    "hailo-8 AI",
    "hailo-10h",
    "hailo AI HAT",
    "hailort inference",
    "hailo edge detection",
    "hailo YOLO",
    "hailo gstreamer",
]


def search_github(query: str, max_results: int = 30) -> list:
    """Search GitHub repos via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "search", "repos", query,
             "--limit", str(max_results),
             "--json", "fullName,url,description,stargazersCount,updatedAt"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []


def main():
    registry = load_yaml(DATA_DIR / "project_registry.yaml")

    # Build set of known URLs
    known_urls = set()
    for project in registry.get("projects", []):
        url = project.get("github_url", "").rstrip("/").lower()
        if url:
            known_urls.add(url)
            # Also add without /tree/... suffix
            if "/tree/" in url:
                known_urls.add(url.split("/tree/")[0])

    # Search
    all_candidates = {}
    for query in SEARCH_QUERIES:
        print(f"Searching: {query}")
        results = search_github(query)
        for repo in results:
            url = repo.get("url", "").rstrip("/").lower()
            if url and url not in known_urls and url not in all_candidates:
                all_candidates[url] = repo

    # Filter and sort by stars
    candidates = sorted(all_candidates.values(),
                        key=lambda r: r.get("stargazersCount", 0),
                        reverse=True)

    print(f"\n{'='*60}")
    print(f"Found {len(candidates)} new repos not in registry:")
    print(f"{'='*60}\n")

    for repo in candidates[:50]:  # Top 50
        name = repo.get("fullName", "")
        stars = repo.get("stargazersCount", 0)
        desc = (repo.get("description") or "")[:80]
        updated = (repo.get("updatedAt") or "")[:10]
        url = repo.get("url", "")
        print(f"  [{stars:>4} stars] {name}")
        print(f"           {desc}")
        print(f"           Updated: {updated}  URL: {url}")
        print()


if __name__ == "__main__":
    main()
