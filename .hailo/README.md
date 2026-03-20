# .hailo/ Directory Index

Agent-facing configuration, instructions, knowledge, and toolsets for building Hailo AI applications. This directory is the primary entry point for AI coding agents working in this repository.

## Directory Structure

```
.hailo/
├── README.md                          ← This file (master index)
├── instructions/                      ← Agent instructions and behavioral guides
├── toolsets/                          ← API references and element catalogs
├── knowledge/                         ← Structured knowledge bases (YAML)
├── memory/                            ← Persistent cross-session knowledge
├── skills/                            ← Skill definitions for agent workflows
├── examples/                          ← Minimal working examples by app type
└── templates/                         ← Scaffolding templates for new apps
```

## Instructions (`instructions/`)

Behavioral guides and development standards for agents.

| File | Description |
|---|---|
| `architecture.md` | Three-tier app architecture (pipeline, standalone, gen-ai), module dependency graph, multiprocessing patterns |
| `coding-standards.md` | Mandatory coding conventions: imports, logging, HEF resolution, CLI parsers, error handling, signal handling |
| `gen-ai-development.md` | Hailo-10H gen AI development guide: VLM/LLM/Whisper patterns, multiprocessing backend, camera and voice integration |
| `gstreamer-pipelines.md` | GStreamer pipeline composition: source/inference/display fragments, callback patterns, pipeline architectures |
| `testing-patterns.md` | Test framework, markers, fixtures, test patterns (sanity, integration, parametrized), running tests |
| `orchestration.md` | Multi-agent orchestration framework: plan-and-execute loops, phase gates, sub-agent delegation patterns |
| `agent-protocols.md` | Behavioral contracts for all agents: context-first execution, phase gates, todo management, memory feedback, recovery |

## Toolsets (`toolsets/`)

API references for frameworks and libraries used in Hailo apps.

| File | Description |
|---|---|
| `hailo-sdk.md` | Hailo Platform SDK API: VDevice, VLM, LLM, Speech2Text, GStreamer buffer API, constants reference |
| `gstreamer-elements.md` | GStreamer elements catalog: Hailo-specific elements (hailonet, hailofilter, etc.), standard elements, helper function mapping |
| `vlm-backend-api.md` | VLM Backend class API: constructor, vlm_inference(), convert_resize_image(), worker process, thread safety |
| `core-framework-api.md` | Core framework API: resolve_hef_path, parsers, logger, HailoInfer, camera utils, GStreamerApp, buffer utils |
| `gen-ai-utilities.md` | Gen AI utilities API: LLM streaming/tool-parsing/context, voice processing (STT, TTS, VAD), agent tools framework |

## Knowledge (`knowledge/`)

Structured knowledge bases in YAML format for agent decision-making.

| File | Description |
|---|---|
| `app_catalog.yaml` | Catalog of all available apps with metadata |
| `best_practices.yaml` | Best practices for Hailo app development |
| `code_snippets.yaml` | Reusable code snippets and patterns |
| `decision_tree.yaml` | Decision trees for choosing app types, models, and architectures |
| `model_compatibility.yaml` | Model compatibility matrix across Hailo architectures |
| `pipeline_patterns.yaml` | GStreamer pipeline composition patterns |
| `troubleshooting.yaml` | Common issues and their solutions |

## Memory (`memory/`)

Persistent cross-session knowledge base. Agents should read at task start and update when discovering new patterns.

| File | Description |
|---|---|
| `gen_ai_patterns.md` | Gen AI app architecture patterns, VLM/LLM gotchas, and proven solutions |

## Examples (`examples/`)

Minimal working examples organized by app type.

| Directory | Description |
|---|---|
| `callback_patterns/` | GStreamer callback implementation examples |
| `display_patterns/` | Display and overlay patterns |
| `minimal_detection/` | Minimal pipeline detection app |
| `minimal_genai/` | Minimal gen AI (VLM/LLM) app |
| `minimal_standalone/` | Minimal standalone inference app |

## Skills (`skills/`)

Skill definitions for agent workflows (e.g., app-builder, profile-pipeline).

## Templates (`templates/`)

Scaffolding templates for creating new apps of each type.
