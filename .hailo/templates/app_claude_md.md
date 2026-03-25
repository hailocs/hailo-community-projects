# App CLAUDE.md Template

Use this template when generating per-app CLAUDE.md files in Phase 3.5.
Replace all `{{placeholders}}` with actual values from the implementation plan.

---

```markdown
# {{App Display Name}}

## What This App Does

{{1-3 paragraph description from Phase 1 requirements. Explain the use case,
what the app detects/processes, and what output it produces.}}

## Architecture

- **Type:** {{Pipeline / Standalone / GenAI}}
- **Pattern:** {{Pipeline pattern from pipeline_patterns.yaml, e.g., source_infer_wrapper_track_display}}
- **Template base:** {{Which official app it was scaffolded from, e.g., detection}}
- **Hardware:** {{hailo8, hailo8l, hailo10h — list all supported}}

### Models

| Model | Task | Default (hailo8) | Default (hailo8l) | Default (hailo10h) |
|-------|------|-------------------|--------------------|--------------------|
| {{model_name}} | {{task}} | {{hef_name or "N/A"}} | {{hef_name or "N/A"}} | {{hef_name or "N/A"}} |

### Postprocess

| .so File | Function | Purpose |
|----------|----------|---------|
| {{so_filename}} | {{function_name}} | {{what it does}} |

## File Structure

| File | Purpose |
|------|---------|
| `{{name}}_pipeline.py` | GStreamerApp subclass with `get_pipeline_string()` |
| `{{name}}.py` | Callback logic and main entry point |
| `__init__.py` | Package marker |
| `README.md` | User documentation |
| `CLAUDE.md` | This file — architecture reference for AI assistants |

## How to Run

```bash
# Activate environment first
source setup_env.sh

# Run with default video input
python community/apps/{{type}}_apps/{{name}}/{{name}}.py

# Run with USB camera
python community/apps/{{type}}_apps/{{name}}/{{name}}.py --input usb

# Run with specific video file
python community/apps/{{type}}_apps/{{name}}/{{name}}.py --input path/to/video.mp4

# Show FPS counter
python community/apps/{{type}}_apps/{{name}}/{{name}}.py --input usb --show-fps

# Use custom frame drawing (enables OpenCV overlay in callback)
python community/apps/{{type}}_apps/{{name}}/{{name}}.py --input usb --use-frame
```

### Custom CLI Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| {{--arg-name}} | {{type}} | {{default}} | {{description}} |

## Pipeline Structure

{{Text diagram of the pipeline flow. Example:}}

```
Source → InferenceWrapper(YOLOv8 + YOLO postprocess) → Tracker → UserCallback → HailoOverlay → Display
```

## Callback Data Available

```python
# In app_callback(element, buffer, user_data):
roi = hailo.get_roi_from_buffer(buffer)

# Detections (if detection model)
detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
for det in detections:
    label = det.get_label()           # e.g., "person", "car"
    confidence = det.get_confidence() # 0.0-1.0
    bbox = det.get_bbox()             # xmin, ymin, width, height (normalized 0-1)

    # Track ID (if tracker in pipeline)
    track = det.get_objects_typed(hailo.HAILO_UNIQUE_ID)
    track_id = track[0].get_id() if len(track) == 1 else 0

    # Landmarks (if pose model)
    landmarks = det.get_objects_typed(hailo.HAILO_LANDMARKS)
    # points = landmarks[0].get_points() — relative to bbox
```

## Key Customization Points

1. **Detection filtering:** In `{{name}}.py`, modify `ALLOWED_LABELS` to change which classes are processed.
2. **Alert thresholds:** Adjust via CLI arguments or modify defaults in the callback class.
3. **Display method:** Change `DISPLAY_PIPELINE()` in `get_pipeline_string()` to switch between hailooverlay, user-frame, or headless modes.
4. **Model swap:** Use `--hef-path <model_name>` to try different models. Use `--list-models` to see options.

## Dependencies

- hailo-apps (core framework, via PYTHONPATH)
- HailoRT (Hailo device runtime)
- TAPPAS GStreamer plugins (hailonet, hailofilter, hailooverlay, etc.)
- OpenCV (cv2) — for frame drawing with --use-frame
{{Add any app-specific dependencies here}}

## Testing

```bash
# Syntax check
python3 -m py_compile community/apps/{{type}}_apps/{{name}}/{{name}}.py
python3 -m py_compile community/apps/{{type}}_apps/{{name}}/{{name}}_pipeline.py

# CLI validation
python community/apps/{{type}}_apps/{{name}}/{{name}}.py --help

# Import check
python3 -c "from community.apps.{{type}}_apps.{{name}}.{{name}}_pipeline import *"

# Functional test with video file
python community/apps/{{type}}_apps/{{name}}/{{name}}.py --input <test_video> --show-fps
```

## Related Apps

- **Template base:** `hailo-apps/hailo_apps/python/{{type}}_apps/{{template_app}}/`
- **Similar community apps:** {{list related community apps}}
- **Alternative approaches:** {{describe when to use alternative apps}}
```
