---
name: hl-profile
description: "Profile GStreamer pipeline performance: auto-setup GST-Shark, profile, analyze bottlenecks, suggest & apply optimizations, run experiments, and learn from results."
argument-hint: "[app-path-or-trace-dir] [options]"
allowed-tools: Bash(python *), Bash(gst-*), Bash(sudo *), Bash(cd *), Read, Write, Edit, Grep, Glob, Agent, AskUserQuestion
---

<!-- Thin Claude Code wrapper — canonical skill doc lives in .hailo/ -->

Read and follow the complete skill documentation at `.hailo/skills/hl-profile.md`.

Scripts are at `.claude/skills/hl-profile/scripts/`:
- `profile_pipeline.py` — Run app with GST-Shark tracing
- `analyze_trace.py` — Parse traces into metrics
- `compare_traces.py` — A/B trace comparison
- `plot_graphs.py` — Generate 4 performance charts
- `ctf_parser.py` — Low-level CTF trace parser
- `knowledge_base.py` — Recipe persistence
- `setup_check.py` — Dependency verification

Also consult:
- `.claude/skills/hl-profile/knowledge/` — Profiling recipes and operational data
- `.hailo/memory/pipeline_optimization.md` — Pipeline performance patterns
