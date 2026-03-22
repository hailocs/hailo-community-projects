#!/usr/bin/env python3
"""Fetch GitHub stats (stars, forks, last commit) for all registered projects.

Usage:
    python fetch_github_stats.py
    python fetch_github_stats.py --update-grades  # Also update freshness/community scores
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    load_yaml, save_yaml, DATA_DIR,
    extract_github_owner_repo, github_api, compute_grade
)


def fetch_stats():
    registry = load_yaml(DATA_DIR / "project_registry.yaml")
    cache_path = DATA_DIR / "github_stats_cache.yaml"
    cache = {"fetched_at": datetime.now().isoformat(), "repos": []}

    for project in registry.get("projects", []):
        url = project.get("github_url", "")
        if not url or "/tree/" in url:
            continue

        result = extract_github_owner_repo(url)
        if not result:
            continue

        owner, repo = result
        print(f"Fetching {owner}/{repo}...", end=" ")

        info = github_api(f"repos/{owner}/{repo}")
        if not info:
            print("FAILED")
            continue

        stars = info.get("stargazers_count", 0)
        forks = info.get("forks_count", 0)
        pushed_at = info.get("pushed_at", "")
        archived = info.get("archived", False)

        print(f"stars={stars} forks={forks} pushed={pushed_at[:10]}")

        cache["repos"].append({
            "id": project["id"],
            "owner": owner,
            "repo": repo,
            "stars": stars,
            "forks": forks,
            "pushed_at": pushed_at,
            "archived": archived,
        })

    save_yaml(cache_path, cache)
    print(f"\nSaved to {cache_path}")
    return cache


def update_grades_from_cache(cache: dict):
    grades_data = load_yaml(DATA_DIR / "project_grades.yaml")
    grades_by_id = {g["id"]: g for g in grades_data.get("projects", [])}

    for repo_data in cache.get("repos", []):
        pid = repo_data["id"]
        if pid not in grades_by_id:
            continue

        grade_entry = grades_by_id[pid]
        scores = grade_entry.get("scores", {})

        # Update community signal
        stars = repo_data.get("stars", 0)
        forks = repo_data.get("forks", 0)
        if stars >= 30 or forks >= 50:
            scores["community_signal"] = 3
        elif stars >= 6:
            scores["community_signal"] = 2
        elif stars >= 1:
            scores["community_signal"] = 1
        else:
            scores["community_signal"] = 0

        # Update freshness
        pushed_at = repo_data.get("pushed_at", "")
        if pushed_at:
            last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - last_push).days
            if age_days <= 30:
                scores["freshness"] = 3
            elif age_days <= 180:
                scores["freshness"] = 2
            elif age_days <= 365:
                scores["freshness"] = 1
            else:
                scores["freshness"] = 0

        # Recompute grade
        grade_entry["scores"] = scores
        letter, score = compute_grade(scores)
        grade_entry["grade"] = letter
        grade_entry["grade_score"] = score
        grade_entry["last_graded"] = datetime.now().strftime("%Y-%m-%d")

    save_yaml(DATA_DIR / "project_grades.yaml", grades_data)
    print("Updated grades with fresh GitHub stats.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-grades", action="store_true")
    args = parser.parse_args()

    cache = fetch_stats()
    if args.update_grades:
        update_grades_from_cache(cache)


if __name__ == "__main__":
    main()
