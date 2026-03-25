# Hailo Community Projects — Copilot Instructions

Community-contributed AI applications for Hailo edge accelerators, built on [hailo-apps](https://github.com/hailo-ai/hailo-apps) (git submodule).

## Quick Start
- Read `.hailo/README.md` for the master index of all shared knowledge
- Read `CLAUDE.md` for project identity and conventions

## Shared Knowledge
All skills, instructions, toolsets, knowledge bases, templates, and examples live in `.hailo/`.
See `.hailo/README.md` for the complete index.

## Two-Repo Layout
- `hailo-apps/` — Git submodule (core framework, READ-ONLY)
- `community/apps/` — Community apps (WRITE here)
- Python imports: `from hailo_apps.python.core...` (via PYTHONPATH)

## Available Skills (hl- prefix)
| Skill | Doc | Type |
|-------|-----|------|
| hl-build-app | `.hailo/skills/hl-build-app.md` | Main build skill |
| hl-build-vlm-app | `.hailo/skills/hl-build-vlm-app.md` | VLM apps |
| hl-build-standalone-app | `.hailo/skills/hl-build-standalone-app.md` | Standalone apps |
| hl-build-agent-app | `.hailo/skills/hl-build-agent-app.md` | Agent apps |
| hl-add-voice | `.hailo/skills/hl-add-voice.md` | Voice capability |
| hl-profile | `.hailo/skills/hl-profile.md` | Profiling |
| hl-contribute | `.hailo/skills/hl-contribute.md` | Community contribution |
| hl-monitoring | `.hailo/skills/hl-monitoring.md` | Continuous monitoring |
| hl-event-detection | `.hailo/skills/hl-event-detection.md` | Event detection |
| hl-camera | `.hailo/skills/hl-camera.md` | Camera integration |
| hl-model-management | `.hailo/skills/hl-model-management.md` | Model management |
| hl-plan-and-execute | `.hailo/skills/hl-plan-and-execute.md` | Orchestration |
| hl-validate | `.hailo/skills/hl-validate.md` | Validation |

## Prompt Templates
See `.github/prompts/hl-*.prompt.md` for ready-to-use build prompts.

## Architecture & Standards
- `.hailo/instructions/architecture.md` — System design
- `.hailo/instructions/coding-standards.md` — Conventions
- `.hailo/instructions/gstreamer-pipelines.md` — Pipeline patterns
- `.hailo/instructions/gen-ai-development.md` — GenAI patterns
- `.hailo/instructions/orchestration.md` — Workflow orchestration
- `.hailo/instructions/agent-protocols.md` — Agent behavior contracts

## API References
- `.hailo/toolsets/hailo-sdk.md` — Hailo SDK
- `.hailo/toolsets/gstreamer-elements.md` — GStreamer elements
- `.hailo/toolsets/vlm-backend-api.md` — VLM Backend
- `.hailo/toolsets/core-framework-api.md` — Core framework
- `.hailo/toolsets/gen-ai-utilities.md` — GenAI utilities

## Memory
Persistent knowledge in `.hailo/memory/`. Read at task start, update when learning.

## Hardware
| Architecture | Value | Use case |
|---|---|---|
| Hailo-8 | `hailo8` | Full performance pipeline + standalone apps |
| Hailo-8L | `hailo8l` | Lower power, compatible model subset |
| Hailo-10H | `hailo10h` | GenAI (LLM, VLM, Whisper) + vision pipelines |
