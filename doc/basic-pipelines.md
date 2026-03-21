# Hailo Pipeline Development Guide

This guide covers how to develop custom applications using the GStreamer pipeline framework provided by [hailo-apps-infra](https://github.com/hailo-ai/hailo-apps-infra). The examples demonstrate object detection, human pose estimation, instance segmentation, and depth estimation using Hailo-8 and Hailo-8L accelerators.

## Installation
See the [Installation Guide](../README.md#installation) in the main README for detailed instructions on setting up your environment.

## Overview

The official pipeline apps are provided by the `hailo-apps-infra` submodule. Community apps follow the same patterns and live in `community/apps/pipeline_apps/`.

```bash
source setup_env.sh

# Official apps (via CLI entry points)
hailo-detect --input usb
hailo-pose --input usb
hailo-seg --input usb
hailo-depth --input usb

# Community apps (run directly)
python community/apps/pipeline_apps/<app_name>/<app_name>.py --input usb
```

## Understanding the Callback Method

Each pipeline app uses a callback method to process data from the GStreamer pipeline. The callback is called whenever a buffer is available from the pipeline. It processes the data, extracts relevant information, and performs actions such as drawing on a frame or printing information.

### User App Callback Class

The `app_callback_class` (from `hailo_apps_infra`) manages user-specific data and state across frames. Subclass it to add your own state:

```python
from hailo_apps.python.core.gstreamer.gstreamer_app import app_callback_class

class MyUserData(app_callback_class):
    def __init__(self):
        super().__init__()
        self.my_counter = 0
```

### Callback Function

The callback function receives the GStreamer buffer and processes Hailo metadata:

```python
import hailo
from gi.repository import Gst

def app_callback(element, buffer, user_data):
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
    for detection in detections:
        label = detection.get_label()
        confidence = detection.get_confidence()
        bbox = detection.get_bbox()
    return Gst.PadProbeReturn.OK
```

**Important:** The callback is blocking — keep it fast. For heavy processing, offload work to a separate thread or process.

## Available Pipelines

### Detection
Object detection using YOLOv8s (Hailo-8L) or YOLOv8m (Hailo-8) by default. Supports all models compiled with HailoRT NMS post-processing. Persons are tracked automatically.

```bash
hailo-detect --input usb
hailo-detect --input usb --use-frame    # Enable Python overlay drawing
hailo-detect --help                      # See all options
```

Additional models available via `hailo-download-resources --all`. For retraining, see the [Retraining Example](https://github.com/hailo-ai/hailo-apps-infra/blob/main/doc/developer_guide/retraining_example.md).

### Pose Estimation
Human pose estimation using YOLOv8 pose models. Each person has 17 keypoints (nose, eyes, ears, shoulders, elbows, wrists, hips, knees, ankles).

```bash
hailo-pose --input usb
```

### Instance Segmentation
Pixel-level segmentation with per-instance masks. Each detection includes a `HAILO_CONF_CLASS_MASK` with the segmentation mask.

```bash
hailo-seg --input usb
```

### Depth Estimation
Depth estimation using `scdepthv3`. Each pixel gets a depth value (relative, normalized, unitless — not real-world distances). The `INFERENCE_PIPELINE_WRAPPER` rescales the 320x256 depth matrix to the original frame resolution.

```bash
hailo-depth --input usb
```

See the original [scdepthv3 paper](https://arxiv.org/abs/2211.03660) for details.

## Building New Apps

### With AI Agents (Recommended)

Use the agentic development tools for guided app building:

- **Claude Code:** `/hl-build-app` — interactive 7-phase workflow (discovery, recommendation, scaffolding, implementation, peer review, testing, optimization)
- **VS Code Copilot:** Use prompt templates in `.github/prompts/`
- **Any agent:** Follow `.hailo/skills/hl-build-app.md`

The agent will scaffold your app in `community/apps/pipeline_apps/`, read framework code from the submodule, and guide you through implementation.

### Manually

1. Start with an existing app as a template (see `hailo-apps-infra/hailo_apps/python/pipeline_apps/`)
2. Create your app directory in `community/apps/pipeline_apps/<your_app>/`
3. Subclass `GStreamerApp` and override `get_pipeline_string()`
4. Write your callback function
5. Add a `README.md`

See the [hailo-apps-infra Developer Guide](https://github.com/hailo-ai/hailo-apps-infra/blob/main/doc/developer_guide/app_development.md) for the full development guide.

## Development Recommendations

- **Start Simple**: Begin with the detection example and customize the callback
- **Minimal Setup**: Run the app, then focus on editing the callback function
- **Consult Knowledge Base**: Check `.hailo/knowledge/` for code snippets, pipeline patterns, and troubleshooting
- **Incremental Complexity**: Start with single-model detection, then add tracking, cascaded models, or tiling as needed
- **Use Framework Helpers**: Always use `SOURCE_PIPELINE()`, `INFERENCE_PIPELINE()`, `DISPLAY_PIPELINE()` instead of raw GStreamer strings
- **Test with Video Files First**: Use `--input path/to/video.mp4` before switching to live camera

## Debugging Tips

### Print Statements
Use `print()` to inspect data flow — frame counts, detection counts, coordinates. For production code, use `get_logger(__name__)` instead.

### ipdb Debugger
Insert breakpoints for interactive debugging:
```python
import ipdb; ipdb.set_trace()
```
Install with `pip install ipdb`.

### VS Code Debugging
See the [VS Code debugging guide](https://community.hailo.ai/t/debugging-raspberry-pi-python-code-using-vs-code/12595) on the Hailo Community Forum.

### Choppy Video Playback
If video is choppy, the pipeline is dropping frames due to slow processing:
- Ensure callback processing is fast and non-blocking
- Disable the callback with `--disable-callback` to isolate the issue
- Use lower resolution or frame rate
- Run `htop` to check CPU usage — if near 100%, reduce workload or use a smaller model
- Consider larger `batch-size` for the Hailo model

### Hailo Monitor
Monitor Hailo device utilization:
```bash
# In one terminal
hailortcli monitor

# In your app terminal
export HAILO_MONITOR=1
python your_app.py --input usb
```

### Pipeline Debugging
See the [hailo-apps-infra Developer Guide](https://github.com/hailo-ai/hailo-apps-infra/blob/main/doc/developer_guide/app_development.md) for GStreamer pipeline debugging techniques, including GST-Shark tracing (also available via `/hl-profile`).

## Environment Setup

Each new terminal session requires:
```bash
source setup_env.sh
```

This activates the virtual environment and sets `PYTHONPATH` for both the project root and hailo-apps-infra.
