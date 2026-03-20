# Hailo Community Projects

Community-contributed AI applications for Hailo edge accelerators, built on top of [hailo-apps-infra](https://github.com/hailo-ai/hailo-apps-infra) (included as a git submodule).

## Two-Repo Layout

```
hailo-community-projects/          ← THIS REPO (community hub)
├── hailo-apps-infra/              ← Git submodule (core framework)
│   ├── hailo_apps/                # Core Python/C++ framework (READ-ONLY reference)
│   │   ├── python/core/           # GStreamerApp, helpers, buffer_utils
│   │   ├── python/pipeline_apps/  # Official pipeline apps
│   │   ├── python/standalone_apps/# Official standalone apps
│   │   ├── python/gen_ai_apps/    # Official GenAI apps
│   │   ├── postprocess/cpp/       # C++ GStreamer plugins
│   │   └── config/                # YAML configs
│   ├── install.sh                 # Main installer
│   └── setup_env.sh               # Infra env setup
├── community/                     ← COMMUNITY APPS (write here)
│   ├── apps/
│   │   ├── pipeline_apps/         # 14 community pipeline apps
│   │   ├── standalone_apps/       # 5 community standalone apps
│   │   └── gen_ai_apps/           # 2 community GenAI apps
│   └── contributions/             # Optimization insights
├── community_projects/            # Legacy community projects
├── install.sh                     # Thin wrapper → hailo-apps-infra/install.sh
├── setup_env.sh                   # Environment setup (activates venv, sets PYTHONPATH)
└── config.yaml                    # Submodule branch/tag config
```

**Rule:** READ from `hailo-apps-infra/hailo_apps/...` for framework code. WRITE new apps to `community/apps/`.

## Quick Reference

```bash
source setup_env.sh                    # Activate environment (always do this first)
./install.sh                           # Full install (delegates to hailo-apps-infra)
git submodule update --init --recursive # Initialize submodule only
```

## Python Imports

```python
# Core framework (from submodule, via PYTHONPATH)
from hailo_apps.python.core.gstreamer.gstreamer_app import GStreamerApp
from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import SOURCE_PIPELINE

# Community apps
from community.apps.pipeline_apps.baby_sleep_monitor import baby_sleep_monitor
```

## Community App Types

### Pipeline Apps (`community/apps/pipeline_apps/`)
Real-time GStreamer video pipelines. Same pattern as infra apps:
- `app.py` (callback + main) + `app_pipeline.py` (GStreamerApp subclass)
- Apps: baby_sleep_monitor, cat_food_monitor, depth_proximity_alert, gesture_mouse, license_plate_reader, line_crossing_counter, multi_camera_store_monitor, multi_entrance_tracker, parking_lot_occupancy, ppe_safety_checker, retail_shelf_analyzer, room_security_monitor, semaphore_translator, workout_rep_counter

### Standalone Apps (`community/apps/standalone_apps/`)
Lightweight HailoRT-only apps, no GStreamer needed.
- Apps: aerial_object_counter, document_text_extractor, lane_departure_warning, photo_enhancer, traffic_light_detector

### GenAI Apps (`community/apps/gen_ai_apps/`)
Hailo-10H generative AI apps.
- Apps: visual_quality_inspector, voice_controlled_camera

## Claude Code Skills

### `/app-builder` — Build new Hailo AI apps
Discover requirements, recommend templates, scaffold, implement, test, profile, and share.
- Knowledge: `.claude/skills/app-builder/knowledge/`
- Templates: `.claude/skills/app-builder/knowledge/templates/`

### `/profile-pipeline` — Profile GStreamer pipeline performance
Auto-setup GST-Shark, profile, analyze bottlenecks, suggest optimizations, run experiments.
- Scripts: `.claude/skills/profile-pipeline/scripts/`
- Knowledge base: `.claude/skills/profile-pipeline/knowledge/knowledge_base.yaml`

### `/contribute-insights` — Share optimization insights
Format findings, sanitize data, submit as PR to hailo-community-projects.

## Memory

Persistent knowledge base in `.claude/memory/`. Consult at task start, update when learning.

## Testing

```bash
cd tests/
pytest -v                              # Run all tests
```

## Hardware

| Architecture | Value | Use case |
|---|---|---|
| Hailo-8 | `hailo8` | Full performance, all pipeline + standalone apps |
| Hailo-8L | `hailo8l` | Lower power, compatible model subset |
| Hailo-10H | `hailo10h` | GenAI (LLM, VLM, Whisper) + vision pipelines |
