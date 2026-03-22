#!/usr/bin/env python3
"""Auto-grade a Hailo community project by analyzing its GitHub repo.

Usage:
    python grade_project.py https://github.com/owner/repo
    python grade_project.py --all   # Re-grade all projects in registry
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    extract_github_owner_repo, github_api, compute_grade,
    load_grades, save_yaml, DATA_DIR
)


def auto_score_project(owner: str, repo: str) -> dict:
    """Auto-score what we can from GitHub API. Returns partial scores dict."""
    scores = {}
    needs_manual = []

    # Fetch repo info
    info = github_api(f"repos/{owner}/{repo}")
    if not info:
        print(f"  Could not fetch repo info for {owner}/{repo}")
        return {"scores": {}, "needs_manual": ["all"], "stars": 0}

    stars = info.get("stargazers_count", 0)
    forks = info.get("forks_count", 0)

    # Community signal
    if stars >= 30 or forks >= 50:
        scores["community_signal"] = 3
    elif stars >= 6:
        scores["community_signal"] = 2
    elif stars >= 1:
        scores["community_signal"] = 1
    else:
        scores["community_signal"] = 0

    # Freshness
    pushed_at = info.get("pushed_at", "")
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
    else:
        needs_manual.append("freshness")

    # Completeness (partial — check for key files)
    tree = github_api(f"repos/{owner}/{repo}/git/trees/HEAD?recursive=1")
    files = set()
    if tree and "tree" in tree:
        files = {item["path"].lower() for item in tree["tree"]}

    has_readme = any(f.endswith("readme.md") for f in files)
    has_requirements = any(f in files for f in ["requirements.txt", "setup.py", "pyproject.toml", "package.json"])
    has_docs = any("doc" in f for f in files)
    has_license = any(f.startswith("license") for f in files)

    completeness_count = sum([has_readme, has_requirements, has_docs, has_license])
    scores["completeness"] = min(completeness_count, 3)

    # Code quality (partial)
    has_tests = any("test" in f for f in files)
    has_ci = any(".github/workflows" in f or ".gitlab-ci" in f for f in files)
    has_lint = any(f in files for f in [".flake8", ".pylintrc", "setup.cfg", ".eslintrc.json", "ruff.toml"])

    quality_count = sum([has_readme, has_tests, has_ci, has_lint])
    scores["code_quality"] = min(quality_count, 3)

    # Hailo integration (keyword search in file names)
    hailo_keywords = {"hailort", "tappas", "hailonet", "gstreamer", "hef", "hailo"}
    hailo_files = sum(1 for f in files if any(kw in f for kw in hailo_keywords))
    if hailo_files >= 5:
        scores["hailo_integration"] = 3
    elif hailo_files >= 2:
        scores["hailo_integration"] = 2
    elif hailo_files >= 1:
        scores["hailo_integration"] = 1
    else:
        needs_manual.append("hailo_integration")
        scores["hailo_integration"] = 1  # default: if it's indexed, it mentions Hailo

    return {"scores": scores, "needs_manual": needs_manual, "stars": stars, "forks": forks}


def grade_single(url: str):
    """Grade a single project and print results."""
    result = extract_github_owner_repo(url)
    if not result:
        print(f"Invalid GitHub URL: {url}")
        return

    owner, repo = result
    print(f"Grading {owner}/{repo}...")

    data = auto_score_project(owner, repo)
    scores = data["scores"]
    grade, score = compute_grade(scores)

    print(f"\n  Stars: {data['stars']}, Forks: {data.get('forks', 0)}")
    print(f"  Scores: {scores}")
    print(f"  Grade: {grade} ({score})")
    if data["needs_manual"]:
        print(f"  Needs manual review: {data['needs_manual']}")

    print(f"\n  YAML entry:")
    print(f"  - id: {repo}")
    print(f"    name: \"{repo}\"")
    print(f"    github_url: \"{url}\"")
    print(f"    scores:")
    for dim, val in scores.items():
        print(f"      {dim}: {val}")
    print(f"    grade: {grade}")
    print(f"    grade_score: {score}")
    print(f"    last_graded: \"{datetime.now().strftime('%Y-%m-%d')}\"")
    print(f"    graded_by: auto")


def main():
    parser = argparse.ArgumentParser(description="Grade Hailo community projects")
    parser.add_argument("url", nargs="?", help="GitHub URL to grade")
    parser.add_argument("--all", action="store_true", help="Re-grade all projects")
    args = parser.parse_args()

    if args.url:
        grade_single(args.url)
    elif args.all:
        grades = load_grades()
        for project in grades.get("projects", []):
            url = project.get("github_url", "")
            result = extract_github_owner_repo(url)
            if result:
                grade_single(url)
                print()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
