---
name: hl-build-app
description: "Build new Hailo AI apps: discover requirements, recommend templates, scaffold, implement, test, profile, and share."
argument-hint: "[use-case-description]"
allowed-tools: Bash(python *), Bash(ls *), Bash(git *), Bash(mkdir *), Bash(cp *), Read, Write, Edit, Grep, Glob, Agent, AskUserQuestion
---

<!-- Thin Claude Code wrapper — canonical skill doc lives in .hailo/ -->

Read and follow the complete skill documentation at `.hailo/skills/hl-build-app.md`.

Also consult:
- `.hailo/knowledge/` — App catalog, decision tree, code snippets, pipeline patterns, model compatibility, troubleshooting, best practices
- `.hailo/templates/` — Pipeline app, standalone app, GenAI app, and CLAUDE.md templates
- `.hailo/examples/` — Minimal runnable examples and callback/display patterns
- `.claude/skills/hl-build-app/scripts/` — validate_app.py, test_scaffold.py, model_check.py, generate_readme.py
