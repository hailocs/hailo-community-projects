# Task: Discover New Hailo Projects

## Goal
Find new Hailo-related repositories on GitHub not yet in the index.

## Steps

1. Run `python internal_agent/scripts/discover_projects.py`
2. Review the candidate list (sorted by stars)
3. For promising projects (5+ stars or interesting use case):
   - Visit the repo and evaluate relevance
   - Determine which section it belongs to
   - Add entry to `project_registry.yaml`
   - Grade it (see `grade_new_projects.md`)
4. Regenerate the index

## Search Queries Used
- hailo raspberry pi, hailo-8 AI, hailo-10h
- hailo AI HAT, hailort inference, hailo edge detection
- hailo YOLO, hailo gstreamer

## Recommended Frequency
Monthly, or when preparing for community events.
