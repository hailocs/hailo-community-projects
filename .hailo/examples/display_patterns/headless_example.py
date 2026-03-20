"""
Display Pattern: Headless / Fakesink Pipeline

Demonstrates running a pipeline without any video display. Useful for:
- Server/embedded deployments without a monitor
- Background processing with data output (CSV, JSON, API)
- Testing and profiling without display overhead

The pipeline uses fakesink instead of DISPLAY_PIPELINE, and the callback
processes detections without any frame drawing.

This is an isolated example showing the pipeline class pattern.
"""
from hailo_apps.python.core.common.core import (
    get_pipeline_parser,
    get_resource_path,
    resolve_hef_path,
)
from hailo_apps.python.core.common.defines import RESOURCES_SO_DIR_NAME
from hailo_apps.python.core.common.hef_utils import get_hef_labels_json
from hailo_apps.python.core.gstreamer.gstreamer_app import GStreamerApp
from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import (
    INFERENCE_PIPELINE,
    INFERENCE_PIPELINE_WRAPPER,
    SOURCE_PIPELINE,
    TRACKER_PIPELINE,
    USER_CALLBACK_PIPELINE,
    DISPLAY_PIPELINE,
)


class GStreamerHeadlessApp(GStreamerApp):
    """Detection pipeline with optional headless mode."""

    def __init__(self, app_callback, user_data, parser=None):
        if parser is None:
            parser = get_pipeline_parser()

        # Add headless mode CLI arg
        parser.add_argument(
            "--headless", action="store_true",
            help="Run without display (fakesink). Use for server/batch mode."
        )
        parser.add_argument(
            "--output-csv", default=None,
            help="Path to CSV file for detection logging."
        )

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
        user_callback = USER_CALLBACK_PIPELINE()

        # Key: switch between display and headless mode
        if self.options_menu.headless:
            # No overlay needed in headless mode — saves CPU
            display = "fakesink sync=false"
        else:
            display = DISPLAY_PIPELINE(
                video_sink=self.video_sink, sync=self.sync, show_fps=self.show_fps
            )

        return (
            f"{source} ! {inference_wrapper} ! {tracker} ! "
            f"{user_callback} ! {display}"
        )


# Usage:
#   python headless_example.py --input video.mp4 --headless --output-csv results.csv
#   python headless_example.py --input usb  # Normal display mode
