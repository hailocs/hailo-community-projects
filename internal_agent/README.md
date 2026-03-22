# Internal Agent Directory

Automation tools for repo maintainers. Used by agents (Claude Code, CI) and humans to maintain the [Hailo Project Index](../community/HAILO_PROJECT_INDEX.md).

## Architecture

```
internal_agent/
├── data/                  # Source of truth (YAML)
│   ├── project_registry.yaml    # All project metadata
│   ├── project_grades.yaml      # Grading scores & results
│   ├── dead_links.yaml          # Link check results
│   └── github_stats_cache.yaml  # Cached GitHub API data
├── tasks/                 # Agent task documents
│   ├── grade_new_projects.md
│   ├── update_github_stats.md
│   ├── check_dead_links.md
│   ├── regenerate_index.md
│   ├── discover_new_projects.md
│   └── audit_grades.md
├── scripts/               # Python automation
│   ├── generate_index.py        # YAML → Markdown renderer
│   ├── grade_project.py         # Auto-grade a project
│   ├── fetch_github_stats.py    # GitHub API stats fetcher
│   ├── check_links.py           # URL validator
│   ├── discover_projects.py     # Find new Hailo repos
│   └── utils.py                 # Shared helpers
└── templates/             # Jinja2 templates for index
    ├── index_header.md
    ├── project_card.md
    └── section.md
```

## Workflow

1. **Discover** — `discover_projects.py` finds new Hailo repos on GitHub
2. **Grade** — `grade_project.py` auto-scores projects, flags for manual review
3. **Register** — Add to `project_registry.yaml` and `project_grades.yaml`
4. **Generate** — `generate_index.py` renders YAML into the public markdown index
5. **Validate** — `check_links.py` ensures all URLs are alive
6. **Refresh** — `fetch_github_stats.py` updates stars/forks/freshness

## Grading System

| Dimension | Weight | Scoring |
|---|---|---|
| Code Quality | 25% | 0-3: no repo → clean code with tests/CI |
| Community Signal | 20% | 0-3: 0 stars → 30+ stars or 50+ forks |
| Freshness | 20% | 0-3: 12+ months stale → active last month |
| Completeness | 20% | 0-3: concept only → full docs + install + demo |
| Hailo Integration | 15% | 0-3: mentions Hailo → multi-model production |

**Grade thresholds:** A (2.5+), B (1.8-2.49), C (1.0-1.79), D (below 1.0)

D-grade projects are excluded from the public index.

## For Agents

- Read `data/project_registry.yaml` for structured project data
- Read `data/project_grades.yaml` for quality signals
- Task docs in `tasks/` are executable instructions
- Never edit the generated markdown directly — edit the YAML, then regenerate
