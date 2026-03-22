# Task: Check for Dead Links

## Goal
Validate all URLs in the project registry are still alive.

## Steps

1. Run `python internal_agent/scripts/check_links.py`
2. Review `internal_agent/data/dead_links.yaml`
3. For each dead link:
   - GitHub 404: Check if repo was renamed/moved/deleted
   - YouTube 404: Find replacement video or remove
   - Demo page 404: Check hailo.ai for updated URL
4. Update `project_registry.yaml` with corrected URLs
5. Regenerate the index

## Quick YouTube Check Only
`python internal_agent/scripts/check_links.py --youtube-only`

## Recommended Frequency
Monthly.
