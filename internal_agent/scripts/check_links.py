#!/usr/bin/env python3
"""Validate all URLs in the project registry.

Usage:
    python check_links.py
    python check_links.py --youtube-only  # Only check YouTube video URLs
"""

import argparse
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_yaml, save_yaml, DATA_DIR, extract_youtube_id


def check_url(url: str, timeout: int = 10) -> tuple[int, str]:
    """Check if URL is reachable. Returns (status_code, status_text)."""
    try:
        req = urllib.request.Request(url, method="HEAD",
                                      headers={"User-Agent": "HailoIndexBot/1.0"})
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.status, "ok"
    except urllib.error.HTTPError as e:
        return e.code, str(e.reason)
    except urllib.error.URLError as e:
        return 0, str(e.reason)
    except Exception as e:
        return 0, str(e)


def check_youtube(video_id: str) -> tuple[int, str]:
    """Check if YouTube video exists via oembed API."""
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    return check_url(url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--youtube-only", action="store_true")
    args = parser.parse_args()

    registry = load_yaml(DATA_DIR / "project_registry.yaml")
    results = {"checked_at": datetime.now().isoformat(), "dead_links": [], "warnings": []}

    for project in registry.get("projects", []):
        pid = project.get("id", "unknown")

        # Check YouTube videos
        for vurl in project.get("video_urls", []):
            vid = extract_youtube_id(vurl)
            if vid:
                status, text = check_youtube(vid)
                if status != 200:
                    print(f"  DEAD YouTube: {vurl} ({status}: {text}) [{pid}]")
                    results["dead_links"].append({
                        "project_id": pid, "url": vurl, "type": "youtube",
                        "status": status, "reason": text
                    })
                else:
                    print(f"  OK: {vurl} [{pid}]")

        if args.youtube_only:
            continue

        # Check GitHub URLs
        github_url = project.get("github_url", "")
        if github_url:
            status, text = check_url(github_url)
            if status not in (200, 301, 302):
                print(f"  DEAD GitHub: {github_url} ({status}: {text}) [{pid}]")
                results["dead_links"].append({
                    "project_id": pid, "url": github_url, "type": "github",
                    "status": status, "reason": text
                })

        # Check official demo URLs
        demo_url = project.get("official_demo_url", "")
        if demo_url:
            status, text = check_url(demo_url)
            if status not in (200, 301, 302):
                print(f"  DEAD Demo: {demo_url} ({status}: {text}) [{pid}]")
                results["dead_links"].append({
                    "project_id": pid, "url": demo_url, "type": "official_demo",
                    "status": status, "reason": text
                })

    output_path = DATA_DIR / "dead_links.yaml"
    save_yaml(output_path, results)
    dead = len(results["dead_links"])
    print(f"\nDone. {dead} dead link(s) found. Saved to {output_path}")


if __name__ == "__main__":
    main()
