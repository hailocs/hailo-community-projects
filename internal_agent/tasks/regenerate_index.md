# Task: Regenerate Project Index

## Goal
Rebuild `community/HAILO_PROJECT_INDEX.md` from the YAML data sources.

## Steps

1. Read `internal_agent/data/project_registry.yaml` — all project metadata
2. Read `internal_agent/data/project_grades.yaml` — quality scores
3. Run `python internal_agent/scripts/generate_index.py`
4. Verify output at `community/HAILO_PROJECT_INDEX.md`
5. Spot-check: confirm D-grade projects are excluded, A-grade appear first

## When to Run
- After any edit to `project_registry.yaml` or `project_grades.yaml`
- After running `fetch_github_stats.py --update-grades`
- After adding new projects
