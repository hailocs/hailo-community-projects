# Task: Update GitHub Stats

## Goal
Refresh cached GitHub stars, forks, and last-commit dates for all projects.

## Steps

1. Run `python internal_agent/scripts/fetch_github_stats.py --update-grades`
2. Review updated grades in `project_grades.yaml` — look for promotions/demotions
3. If any project crossed a grade boundary (e.g., C→B), verify manually
4. Regenerate the index

## What Gets Updated
- `github_stats_cache.yaml` — raw stats
- `project_grades.yaml` — community_signal and freshness scores auto-updated
- Grade letters recalculated

## Recommended Frequency
Weekly or bi-weekly.
