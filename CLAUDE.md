# Hailo Community Projects

Community-contributed AI applications for Hailo edge accelerators, built on top of [hailo-apps-infra](https://github.com/hailo-ai/hailo-apps-infra) (included as a git submodule).

## Two-Repo Layout

```
hailo-community-projects/          ← THIS REPO (community hub)
├── hailo-apps-infra/              ← Git submodule (core framework, READ-ONLY)
│   ├── hailo_apps/                # Core Python/C++ framework
│   └── ...
├── community/                     ← COMMUNITY APPS (write here)
│   ├── apps/
│   │   ├── pipeline_apps/         # 14 community pipeline apps
│   │   ├── standalone_apps/       # 5 community standalone apps
│   │   └── gen_ai_apps/           # 2 community GenAI apps
│   └── contributions/             # Optimization insights
├── .hailo/                        ← SHARED KNOWLEDGE (all platforms)
│   ├── README.md                  # Master index
│   ├── instructions/              # Architecture & standards
│   ├── skills/                    # Platform-neutral skill docs (hl- prefix)
│   ├── toolsets/                  # API references
│   ├── knowledge/                 # YAML knowledge bases
│   ├── memory/                    # Persistent cross-session knowledge
│   ├── templates/                 # Scaffold templates
│   └── examples/                  # Runnable code examples
├── .claude/skills/                ← Claude Code slash commands (thin wrappers → .hailo/)
├── .github/prompts/               ← Copilot prompt files (hl- prefixed)
├── .cursor/rules                  ← Cursor entry point (→ .hailo/)
└── community_projects/            # Legacy community projects
```

**Rule:** READ from `hailo-apps-infra/hailo_apps/...` for framework code. WRITE new apps to `community/apps/`.

## Quick Reference

```bash
source setup_env.sh                    # Activate environment (always do this first)
./install.sh                           # Full install (delegates to hailo-apps-infra)
git submodule update --init --recursive # Initialize submodule only
```

## Shared Knowledge

All skills, instructions, toolsets, knowledge bases, templates, and examples live in `.hailo/`.
Read `.hailo/README.md` for the complete master index.

## Python Imports

```python
# Core framework (from submodule, via PYTHONPATH)
from hailo_apps.python.core.gstreamer.gstreamer_app import GStreamerApp
from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import SOURCE_PIPELINE

# Community apps
from community.apps.pipeline_apps.baby_sleep_monitor import baby_sleep_monitor
```

## Skills (hl- prefix)

### Claude Code Slash Commands
| Command | Description |
|---------|-------------|
| `/hl-build-app` | Build new Hailo AI apps (main builder) |
| `/hl-build-vlm-app` | Build VLM image understanding apps |
| `/hl-build-standalone-app` | Build standalone HailoRT apps |
| `/hl-build-agent-app` | Build AI agent apps with tool calling |
| `/hl-add-voice` | Add speech-to-text / text-to-speech |
| `/hl-profile` | Profile GStreamer pipeline performance |
| `/hl-contribute` | Share optimization insights with community |

### Reference Skills (docs in `.hailo/skills/`, consulted by agents)
| Skill | Description |
|-------|-------------|
| `hl-monitoring` | Continuous video monitoring pattern |
| `hl-event-detection` | Event detection from VLM responses |
| `hl-camera` | Camera setup & management |
| `hl-model-management` | HEF model management |
| `hl-plan-and-execute` | Orchestrated workflow pattern |
| `hl-validate` | Validation & testing |

## Community App Types

### Pipeline Apps (`community/apps/pipeline_apps/`)
Real-time GStreamer video pipelines. Same pattern as infra apps:
- `app.py` (callback + main) + `app_pipeline.py` (GStreamerApp subclass)

### Standalone Apps (`community/apps/standalone_apps/`)
Lightweight HailoRT-only apps, no GStreamer needed.

### GenAI Apps (`community/apps/gen_ai_apps/`)
Hailo-10H generative AI apps.

## Hardware

| Architecture | Value | Use case |
|---|---|---|
| Hailo-8 | `hailo8` | Full performance, all pipeline + standalone apps |
| Hailo-8L | `hailo8l` | Lower power, compatible model subset |
| Hailo-10H | `hailo10h` | GenAI (LLM, VLM, Whisper) + vision pipelines |

## Memory

Persistent knowledge base in `.hailo/memory/`. Consult at task start, update when learning.

## Testing

```bash
cd tests/
pytest -v                              # Run all tests
```
