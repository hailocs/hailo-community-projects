"""
Minimal Detection Pipeline App — Callback File

The simplest possible pipeline detection app. Detects objects using YOLOv8,
prints a summary every 30 frames, and optionally draws on the frame.

Usage:
    source setup_env.sh
    python community/apps/pipeline_apps/detection_example/detection_example.py
    python community/apps/pipeline_apps/detection_example/detection_example.py --input usb --show-fps
    python community/apps/pipeline_apps/detection_example/detection_example.py --input video.mp4 --use-frame
"""
import os
os.environ["GST_PLUGIN_FEATURE_RANK"] = "vaapidecodebin:NONE"

import gi
gi.require_version("Gst", "1.0")
import cv2
import hailo
from gi.repository import Gst

from detection_example_pipeline import GStreamerDetectionExampleApp
from hailo_apps.python.core.common.buffer_utils import (
    get_caps_from_pad,
    get_numpy_from_buffer,
)
from hailo_apps.python.core.gstreamer.gstreamer_app import app_callback_class


# ------------------------------------------------------------------------------
# Callback state — persists across frames
# ------------------------------------------------------------------------------
class DetectionCallbackData(app_callback_class):
    def __init__(self):
        super().__init__()
        self.total_detections = 0


# ------------------------------------------------------------------------------
# Callback — called for every frame
# ------------------------------------------------------------------------------
def app_callback(element, buffer, user_data):
    """Process each frame: extract detections, optionally draw on frame."""
    if buffer is None:
        return

    frame_idx = user_data.get_count()

    # Extract detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Count detections this frame
    user_data.total_detections += len(detections)

    # Optional: draw on frame when --use-frame is passed
    if user_data.use_frame:
        pad = element.get_static_pad("src")
        fmt, width, height = get_caps_from_pad(pad)
        if fmt is not None and width is not None and height is not None:
            frame = get_numpy_from_buffer(buffer, fmt, width, height)
            cv2.putText(
                frame,
                f"Frame {frame_idx}: {len(detections)} detections",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            user_data.set_frame(frame)

    # Print summary every 30 frames (avoid flooding terminal)
    if frame_idx % 30 == 0:
        labels = [d.get_label() for d in detections]
        print(f"Frame {frame_idx}: {len(detections)} detections — {labels}")


# ------------------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------------------
def main():
    user_data = DetectionCallbackData()
    app = GStreamerDetectionExampleApp(app_callback, user_data)
    app.run()


if __name__ == "__main__":
    main()
