# Pipeline Optimization — Memory

## Key Defaults (reference these before tuning)

| Component | Default | Notes |
|---|---|---|
| `QUEUE()` | max_size_buffers=3, leaky=no | Standard pipeline queue |
| `INFERENCE_PIPELINE_WRAPPER` bypass | max_size_buffers=20 | Higher to prevent stalls |
| `GStreamerApp` pipeline_latency | 300ms | |
| `SOURCE_PIPELINE` videoscale | n-threads=2 | |
| `SOURCE_PIPELINE` videoconvert | n-threads=3 | |

## Common Bottleneck Fixes

### hailonet Inside hailocropper (CRITICAL)
**Pattern**: `hailonet` with `batch-size > 1` inside a `hailocropper` path has variable crop count per frame.
**Symptom**: High mean proctime on hailonet, high queue fill on bypass queue, jittery latency.
**Fix**: Add `scheduler-timeout-ms=<1000/target_fps>` (e.g., 33 for 30fps).
**Why**: Without timeout, batch waits for crops that may never arrive. With timeout, fires partial batches.
**Impact**: In gesture_detection, latency dropped from 257ms → 93ms (64% reduction).

### videoconvert Slow
**Fix**: Increase `n-threads` to 3-4. Consider NV12 format to reduce conversion overhead.

### videoscale Slow
**Fix**: Increase `n-threads` to 3-4. Reduce source resolution if possible.

### hailonet Slow
**Fix**: Tune batch-size (no fixed constraint in HEF — always configurable at runtime), scheduler-timeout-ms.

### CPU > 90%
**Fix**: Reduce resolution or frame rate. Consider capping FPS below maximum if use case allows.

### Queue Fill > 70%
**Fix**: Increase `max_size_buffers` on that queue.

### Element P95 > 2x Mean (High Jitter)
**Diagnosis**: Usually means downstream element is periodically blocking.
**Fix**: If upstream of hailonet → fix hailonet scheduler first. If standalone → add absorption queue.

## NEVER Do This

- **NEVER suggest leaky queues between cropper/aggregator pairs** — leaky queues in these paths cause frame count misalignment and pipeline hangs. The aggregator expects matching frame counts.

## TAPPAS Coordinate Spaces & scaling_bbox

### The Problem
`INFERENCE_PIPELINE_WRAPPER` sets a non-identity `scaling_bbox` on ROI (letterbox transform).

### Key Facts
- `set_scaling_bbox(bbox)` **ACCUMULATES** (composes), NOT a simple setter
- `clear_scaling_bbox()` resets to identity (0,0,1,1)
- `hailooverlay` applies scaling_bbox to detection bboxes but NOT to landmarks → mismatch
- Multiple INFERENCE_PIPELINE_WRAPPERs compound their scaling_bboxes

### Fix
If creating new detections in frame-absolute coords after a wrapper: `roi->clear_scaling_bbox()`

## FPS Optimization Strategy

Many users default to 30 FPS but don't actually need it:
- Security/monitoring: 10-15 FPS is sufficient
- Analytics: 15-20 FPS is sufficient
- Interactive demos: 20-25 FPS is sufficient
- Only real-time video display needs 30 FPS

Reducing FPS proportionally reduces CPU usage and improves stability.

## Important Constraints

- **NEVER suggest leaky queues mid-pipeline** — leaky queues between cropper/aggregator pairs cause frame count misalignment and pipeline hangs. The aggregator expects matching frame counts on bypass and crop paths.

## Profiling UX & Graph Generation

- After analysis, always offer to generate performance graphs (bar chart of proctime, latency waterfall, queue fill). Users prefer visual data.
- **Always open generated graphs** with `xdg-open <path>` so the user can see them on screen. Don't just embed in chat — open the file.
- Graph templates script: `.hailo/profile-pipeline/scripts/plot_graphs.py`
  - `python plot_graphs.py <trace_dir> --open` — generates all 4 graphs and opens them
  - Can also import: `from plot_graphs import generate_all, plot_proctime, plot_npu_breakdown, plot_latency_waterfall, plot_queue_levels`
  - Waterfall uses inline labels (name + duration on each bar segment)
  - Queue chart auto-colors by pipeline section (pose=red, palm=orange, cropper=purple, etc.)

## Profiling Quick Reference
- Profiler skill: `/profile-pipeline` (see `.hailo/profile-pipeline/SKILL.md`)
- Scripts: `.hailo/profile-pipeline/scripts/`
- Knowledge base: `.hailo/profile-pipeline/knowledge/knowledge_base.yaml`

## Discovered Patterns
(Updated by `/profile-pipeline learn` after experiments)
