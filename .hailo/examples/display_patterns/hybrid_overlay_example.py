"""
Display Pattern: Hybrid Overlay (hailooverlay_community + user-frame)

Demonstrates the hybrid display pattern where:
1. hailooverlay_community renders bboxes/labels at C++ speed IN the pipeline
2. The user callback receives the already-annotated frame
3. Callback adds custom extras (zones, counters, alert text) on top

Key: The overlay element MUST come BEFORE the user callback in the pipeline.

This is an isolated example showing the pipeline class and callback pattern.
"""
import cv2
import hailo

from hailo_apps.python.core.common.buffer_utils import (
    get_caps_from_pad,
    get_numpy_from_buffer,
)
from hailo_apps.python.core.common.core import (
    get_pipeline_parser,
    get_resource_path,
    resolve_hef_path,
)
from hailo_apps.python.core.common.defines import RESOURCES_SO_DIR_NAME
from hailo_apps.python.core.common.hef_utils import get_hef_labels_json
from hailo_apps.python.core.gstreamer.gstreamer_app import (
    GStreamerApp,
    app_callback_class,
)
from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import (
    INFERENCE_PIPELINE,
    INFERENCE_PIPELINE_WRAPPER,
    OVERLAY_PIPELINE,
    QUEUE,
    SOURCE_PIPELINE,
    TRACKER_PIPELINE,
    USER_CALLBACK_PIPELINE,
)


class GStreamerHybridOverlayApp(GStreamerApp):
    """Pipeline with hailooverlay_community before callback."""

    def __init__(self, app_callback, user_data, parser=None):
        if parser is None:
            parser = get_pipeline_parser()

        super().__init__(parser, user_data)

        if self.batch_size == 1:
            self.batch_size = 2

        self.hef_path = resolve_hef_path(
            self.hef_path, app_name="detection", arch=self.arch
        )
        self.post_process_so = get_resource_path(
            "detection", RESOURCES_SO_DIR_NAME, self.arch,
            "libyolo_hailortpp_postprocess.so"
        )
        self.post_function_name = "filter_letterbox"
        self.labels_json = get_hef_labels_json(self.hef_path)

        self.app_callback = app_callback
        self.thresholds_str = (
            "nms-score-threshold=0.3 "
            "nms-iou-threshold=0.45 "
            "output-format-type=HAILO_FORMAT_TYPE_FLOAT32"
        )
        self.create_pipeline()

    def get_pipeline_string(self):
        source = SOURCE_PIPELINE(
            video_source=self.video_source,
            video_width=self.video_width,
            video_height=self.video_height,
            frame_rate=self.frame_rate,
            sync=self.sync,
        )
        inference = INFERENCE_PIPELINE(
            hef_path=self.hef_path,
            post_process_so=self.post_process_so,
            post_function_name=self.post_function_name,
            batch_size=self.batch_size,
            config_json=self.labels_json,
            additional_params=self.thresholds_str,
        )
        inference_wrapper = INFERENCE_PIPELINE_WRAPPER(inference)
        tracker = TRACKER_PIPELINE(class_id=-1)

        # OVERLAY BEFORE CALLBACK — bboxes rendered at C++ speed
        overlay = OVERLAY_PIPELINE(community=True)
        user_callback = USER_CALLBACK_PIPELINE()

        # Manual display (no DISPLAY_PIPELINE since overlay is separate)
        pipeline = (
            f"{source} ! {inference_wrapper} ! {tracker} ! "
            f"{overlay} ! {user_callback} ! "
            f"videoconvert ! {QUEUE()} ! "
            f"fpsdisplaysink video-sink={self.video_sink} sync={self.sync} "
            f"text-overlay={self.show_fps}"
        )
        return pipeline


class HybridCallbackData(app_callback_class):
    """Callback state for hybrid overlay example."""
    def __init__(self):
        super().__init__()
        self.person_count = 0


def app_callback(element, buffer, user_data):
    """
    Frame already has bboxes drawn by hailooverlay_community.
    We just add custom extras: a person counter and a status bar.
    """
    if buffer is None:
        return

    frame_idx = user_data.get_count()
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    person_count = sum(1 for d in detections if d.get_label() == "person")
    user_data.person_count = person_count

    # Draw custom extras on the already-annotated frame
    if user_data.use_frame:
        pad = element.get_static_pad("src")
        fmt, width, height = get_caps_from_pad(pad)
        if fmt and width and height:
            frame = get_numpy_from_buffer(buffer, fmt, width, height)

            # Bboxes are ALREADY on the frame from hailooverlay_community!
            # Just add custom overlay text:
            cv2.putText(
                frame, f"People: {person_count}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2,
            )

            # Status bar at bottom
            bar_y = height - 40
            cv2.rectangle(frame, (0, bar_y), (width, height), (0, 0, 0), -1)
            cv2.putText(
                frame, f"Frame {frame_idx} | Detections: {len(detections)}",
                (10, height - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
            )

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            user_data.set_frame(frame)

    if frame_idx % 30 == 0:
        print(f"Frame {frame_idx}: {person_count} people, {len(detections)} total")
