# Task: Quarterly Grade Audit

## Goal
Re-evaluate all project grades to ensure accuracy and fairness.

## Steps

1. Run `python internal_agent/scripts/fetch_github_stats.py --update-grades`
2. Review all A-grade projects — are they still active and high quality?
3. Review D-grade projects — have any improved enough to include?
4. Check for grade inflation (too many A's means criteria too loose)
5. Update manual scores (code_quality, completeness, hailo_integration) where needed
6. Regenerate the index

## Target Distribution
- A: ~15% (top showcase projects)
- B: ~35% (solid, recommended)
- C: ~40% (functional but limited)
- D: ~10% (excluded from public index)

## Recommended Frequency
Quarterly.
