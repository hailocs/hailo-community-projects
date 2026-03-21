# .hailo/ — Shared Agentic Knowledge

Platform-neutral knowledge base for building Hailo AI applications. This directory is the canonical source of truth for all AI coding agents (Claude Code, VS Code Copilot, Cursor, or any LLM-based agent).

## Directory Structure

```
.hailo/
├── README.md                          ← This file (master index)
├── instructions/                      ← Architecture & development standards
├── skills/                            ← Step-by-step workflow guides (hl- prefix)
├── toolsets/                          ← API references
├── knowledge/                         ← Structured knowledge bases (YAML)
├── memory/                            ← Persistent cross-session knowledge
├── templates/                         ← Scaffold templates for new apps
└── examples/                          ← Minimal runnable examples
```

## Instructions (`instructions/`)

Architecture and development standards for building Hailo apps.

| File | Description |
|---|---|
| `architecture.md` | Three-tier app architecture (pipeline, standalone, gen-ai), module dependency graph, multiprocessing patterns |
| `coding-standards.md` | Mandatory coding conventions: imports, logging, HEF resolution, CLI parsers, error handling, signal handling |
| `gen-ai-development.md` | Hailo-10H gen AI guide: VLM/LLM/Whisper patterns, multiprocessing backend, camera and voice integration |
| `gstreamer-pipelines.md` | GStreamer pipeline composition: source/inference/display fragments, callback patterns, pipeline architectures |
| `testing-patterns.md` | Test framework, markers, fixtures, test patterns (sanity, integration, parametrized) |
| `orchestration.md` | Multi-agent orchestration: plan-and-execute loops, phase gates, sub-agent delegation |
| `agent-protocols.md` | 9 behavioral contracts for agents: context-first execution, phase gates, todo management, memory feedback, recovery |

## Skills (`skills/`)

Step-by-step workflow guides for agents. All use the `hl-` prefix.

### Build Skills
| File | Description |
|---|---|
| `hl-build-app.md` | Main app builder — 7-phase workflow: discovery, recommendation, scaffolding, implementation, peer review, testing, optimization |
| `hl-build-vlm-app.md` | Build Vision-Language Model apps for Hailo-10H (image understanding, scene analysis) |
| `hl-build-standalone-app.md` | Build standalone HailoRT inference apps (no GStreamer, full Python control) |
| `hl-build-agent-app.md` | Build AI agent apps with LLM tool calling |
| `hl-add-voice.md` | Add speech-to-text (Whisper) and text-to-speech (Piper) to any app |

### Operational Skills
| File | Description |
|---|---|
| `hl-profile.md` | Profile GStreamer pipeline performance with GST-Shark, analyze bottlenecks, run A/B experiments |
| `hl-contribute.md` | Format and share optimization insights as community contributions |

### Pattern Skills (Reference)
| File | Description |
|---|---|
| `hl-monitoring.md` | Continuous video monitoring with periodic VLM analysis |
| `hl-event-detection.md` | Detect specific events from VLM responses with structured logging |
| `hl-camera.md` | Camera setup, discovery, and management (USB, RPi, RTSP) |
| `hl-model-management.md` | HEF model resolution, download, and configuration |

### Meta Skills
| File | Description |
|---|---|
| `hl-plan-and-execute.md` | Orchestrated multi-phase workflow: plan, delegate, execute, gate |
| `hl-validate.md` | 5-level validation: structural, imports, functional, conventions, lint |

## Toolsets (`toolsets/`)

API references for frameworks and libraries used in Hailo apps.

| File | Description |
|---|---|
| `hailo-sdk.md` | Hailo Platform SDK: VDevice, VLM, LLM, Speech2Text, GStreamer buffer API, constants |
| `gstreamer-elements.md` | GStreamer elements catalog: Hailo-specific elements, standard elements, helper function mapping |
| `vlm-backend-api.md` | VLM Backend class: constructor, vlm_inference(), convert_resize_image(), thread safety |
| `core-framework-api.md` | Core framework: resolve_hef_path, parsers, logger, HailoInfer, camera utils, GStreamerApp, buffer utils |
| `gen-ai-utilities.md` | Gen AI utilities: LLM streaming/tool-parsing/context, voice processing (STT, TTS, VAD), agent tools framework |

## Knowledge (`knowledge/`)

Structured knowledge bases in YAML format for agent decision-making.

| File | Description |
|---|---|
| `app_catalog.yaml` | Catalog of 26+ official and 21 community apps with metadata, use cases, and features |
| `decision_tree.yaml` | Decision tree and 40+ keyword shortcuts for app selection |
| `code_snippets.yaml` | Reusable callback patterns: pose angles, line crossing, zones, tracking, alerts, display |
| `pipeline_patterns.yaml` | 8 GStreamer pipeline architecture patterns with code examples |
| `model_compatibility.yaml` | Model/HEF compatibility matrix across Hailo-8, Hailo-8L, Hailo-10H |
| `best_practices.yaml` | 15+ lessons learned from building 20+ Hailo apps |
| `troubleshooting.yaml` | 20+ common errors with symptoms, causes, and step-by-step fixes |
| `knowledge_base.yaml` | Merged operational knowledge: tuning recipes, bottleneck patterns, gen AI recipes, insights |

## Memory (`memory/`)

Persistent cross-session knowledge base. Read at task start, update when discovering new patterns.

| File | When to Read |
|---|---|
| `MEMORY.md` | Always — unified index of all memory files |
| `gen_ai_patterns.md` | Building Gen AI apps — VLM/LLM architecture, multiprocessing, token streaming, gotchas |
| `pipeline_optimization.md` | Profiling or optimizing pipelines — key defaults, bottleneck fixes, FPS strategy |
| `camera_and_display.md` | Camera or display work — USB/RPi/RTSP setup, BGR/RGB, OpenCV patterns |
| `hailo_platform_api.md` | Using HailoRT directly — VDevice, HEF resolution, SDK API patterns |
| `common_pitfalls.md` | Always useful — import errors, signal handling, multiprocessing, OpenCV, GStreamer gotchas |
| `gesture_detection.md` | Gesture/hand tracking — Blaze model mapping, scaling_bbox bugs, coordinate spaces |
| `tappas_coordinate_spaces.md` | Working with overlays/coordinates — scaling_bbox accumulation, hailooverlay asymmetry |
| `audio_issues.md` | Voice/audio apps — AudioPlayer race conditions, microphone setup, PulseAudio |

## Templates (`templates/`)

Annotated scaffold templates for creating new apps.

| File | Description |
|---|---|
| `pipeline_app.md` | Full GStreamer pipeline app template with imports, class structure, pipeline building |
| `standalone_app.md` | HailoRT standalone app template with HailoInfer pattern |
| `genai_app.md` | GenAI LLM/VLM/STT app template with resource management |
| `app_claude_md.md` | Per-app CLAUDE.md generator template |

## Examples (`examples/`)

Minimal runnable examples organized by category.

| Directory | Contents |
|---|---|
| `minimal_detection/` | Simplest pipeline detection app — `detection_example.py` + `detection_example_pipeline.py` |
| `minimal_standalone/` | Simplest standalone HailoRT app — `standalone_example.py` |
| `minimal_genai/` | Simplest GenAI LLM chat app — `genai_example.py` |
| `callback_patterns/` | Isolated callback examples: tracking, zone counting, line crossing, pose analysis |
| `display_patterns/` | Display method examples: headless/fakesink, hybrid overlay, web UI |

## Platform Integration

This directory is read by all supported platforms:

| Platform | Entry Point | How It Accesses .hailo/ |
|----------|-------------|------------------------|
| Claude Code | `CLAUDE.md` → `.claude/skills/hl-*/SKILL.md` | SKILL.md files reference `.hailo/` paths |
| VS Code Copilot | `.github/copilot-instructions.md` | Points to `.hailo/` directory |
| Cursor | `.cursor/rules` | Points to `.hailo/` directory |
| Any AI agent | Direct | Read `.hailo/` files directly |
