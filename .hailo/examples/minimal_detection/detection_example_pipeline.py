"""
Minimal Detection Pipeline — Pipeline Class

GStreamerApp subclass that builds a standard detection pipeline:
  Source -> InferenceWrapper(YOLOv8 + YOLO postprocess) -> Tracker -> Callback -> Display
"""
from pathlib import Path

import setproctitle

from hailo_apps.python.core.common.core import (
    get_pipeline_parser,
    get_resource_path,
    handle_list_models_flag,
    resolve_hef_path,
)
from hailo_apps.python.core.common.defines import RESOURCES_SO_DIR_NAME
from hailo_apps.python.core.common.hef_utils import get_hef_labels_json
from hailo_apps.python.core.gstreamer.gstreamer_app import (
    GStreamerApp,
    app_callback_class,
    dummy_callback,
)
from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import (
    DISPLAY_PIPELINE,
    INFERENCE_PIPELINE,
    INFERENCE_PIPELINE_WRAPPER,
    SOURCE_PIPELINE,
    TRACKER_PIPELINE,
    USER_CALLBACK_PIPELINE,
)


class GStreamerDetectionExampleApp(GStreamerApp):
    def __init__(self, app_callback, user_data, parser=None):
        if parser is None:
            parser = get_pipeline_parser()

        parser.add_argument(
            "--labels-json", default=None, help="Path to custom labels JSON file"
        )

        handle_list_models_flag(parser, "detection")

        super().__init__(parser, user_data)

        # Model configuration
        if self.batch_size == 1:
            self.batch_size = 2

        nms_score_threshold = 0.3
        nms_iou_threshold = 0.45

        # Resolve resources
        self.hef_path = resolve_hef_path(
            self.hef_path, app_name="detection", arch=self.arch
        )
        self.post_process_so = get_resource_path(
            "detection", RESOURCES_SO_DIR_NAME, self.arch,
            "libyolo_hailortpp_postprocess.so"
        )
        self.post_function_name = "filter_letterbox"

        self.labels_json = self.options_menu.labels_json
        if self.labels_json is None:
            self.labels_json = get_hef_labels_json(self.hef_path)

        # Validate resources
        if self.hef_path is None or not Path(self.hef_path).exists():
            raise FileNotFoundError(f"HEF not found: {self.hef_path}")
        if self.post_process_so is None or not Path(self.post_process_so).exists():
            raise FileNotFoundError(f"Postprocess .so not found: {self.post_process_so}")

        self.app_callback = app_callback
        self.thresholds_str = (
            f"nms-score-threshold={nms_score_threshold} "
            f"nms-iou-threshold={nms_iou_threshold} "
            f"output-format-type=HAILO_FORMAT_TYPE_FLOAT32"
        )

        setproctitle.setproctitle("Hailo Detection Example")
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
        display = DISPLAY_PIPELINE(
            video_sink=self.video_sink, sync=self.sync, show_fps=self.show_fps
        )

        return (
            f"{source} ! {inference_wrapper} ! {tracker} ! "
            f"{user_callback} ! {display}"
        )


def main():
    user_data = app_callback_class()
    app = GStreamerDetectionExampleApp(dummy_callback, user_data)
    app.run()


if __name__ == "__main__":
    main()
