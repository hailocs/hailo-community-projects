---
name: hl-build-agent-app
description: "Build an AI agent application with tool calling using Hailo LLM."
argument-hint: "[agent-app-description]"
allowed-tools: Bash(python *), Bash(ls *), Bash(git *), Bash(mkdir *), Bash(cp *), Read, Write, Edit, Grep, Glob, Agent, AskUserQuestion
---

<!-- Thin Claude Code wrapper — canonical skill doc lives in .hailo/ -->

Read and follow the complete skill documentation at `.hailo/skills/hl-build-agent-app.md`.

Also consult:
- `.hailo/toolsets/gen-ai-utilities.md` — LLM utilities, tool parsing, agent framework
- `.hailo/skills/hl-add-voice.md` — For voice-enabled agents
- `.hailo/toolsets/hailo-sdk.md` — Hailo SDK reference
