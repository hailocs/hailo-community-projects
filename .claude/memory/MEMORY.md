# Hailo Community Projects - Memory

## Project Structure
- Repo root: `/home/giladn/tappas_apps/repos/hailo-community-projects`
- Core framework (submodule): `hailo-apps-infra/hailo_apps/` (READ-ONLY reference)
- Community apps: `community/apps/{pipeline_apps,standalone_apps,gen_ai_apps}/`
- C++ postprocess: `hailo-apps-infra/hailo_apps/postprocess/cpp/`
- GStreamer helpers: `hailo-apps-infra/hailo_apps/python/core/gstreamer/gstreamer_helper_pipelines.py`
- Resources installed to: `/usr/local/hailo/resources/`

## Build Commands
- Activate env: `source setup_env.sh`
- Install: `./install.sh` (delegates to hailo-apps-infra)
- Compile C++ postprocess: `hailo-compile-postprocess`
- Full post-install: `hailo-post-install`

## Key Patterns
- Pipeline apps follow: `app.py` (callback + main) + `app_pipeline.py` (GStreamerApp subclass)
- New apps go in `community/apps/`, NOT in `hailo-apps-infra/hailo_apps/python/`
- Python imports use `hailo_apps.python...` (via PYTHONPATH), file paths use `hailo-apps-infra/hailo_apps/...`

## Memory Index
- [gesture_detection.md](gesture_detection.md) — Gesture detection app notes, bugs found & fixed
- [tappas_coordinate_spaces.md](tappas_coordinate_spaces.md) — TAPPAS scaling_bbox, coordinate spaces
- [pipeline_profiling.md](pipeline_profiling.md) — Pipeline profiler notes, bottleneck patterns
- [audio_issues.md](audio_issues.md) — GenAI voice assistant audio issues
