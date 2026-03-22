# Task: Grade New Projects

## Goal
Score ungraded projects in the registry using the grading system.

## Steps

1. Read `internal_agent/data/project_registry.yaml`
2. Read `internal_agent/data/project_grades.yaml`
3. Find projects in registry that have no entry in grades
4. For each ungraded project with a GitHub URL:
   - Run `python internal_agent/scripts/grade_project.py <url>`
   - Review the auto-generated scores
   - Manually adjust `hailo_integration` and `code_quality` if needed
5. Add the grade entry to `project_grades.yaml`
6. Regenerate the index

## Grading Criteria

| Dimension | Weight | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| Code Quality | 25% | No repo | Repo exists | README + structure | Tests, CI, clean code |
| Community Signal | 20% | 0 stars | 1-5 stars | 6-30 stars | 30+ stars |
| Freshness | 20% | 12+ months | 6-12 months | 1-6 months | Last month |
| Completeness | 20% | Concept only | Partial | Works, limited docs | Full docs + demo |
| Hailo Integration | 15% | Mentions Hailo | Basic HailoRT | TAPPAS/GStreamer | Multi-model, production |

**Thresholds:** A (2.5+), B (1.8-2.49), C (1.0-1.79), D (<1.0)
