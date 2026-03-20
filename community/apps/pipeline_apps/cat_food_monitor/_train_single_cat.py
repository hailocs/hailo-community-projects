#!/usr/bin/env python3
"""Train a single cat image through the CLIP pipeline and store embedding in LanceDB."""
import os, sys, time, uuid
os.environ["GST_PLUGIN_FEATURE_RANK"] = "vaapidecodebin:NONE"

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import numpy as np

import hailo
from hailo_apps.python.core.common.db_handler import DatabaseHandler, Record
from hailo_apps.python.core.common.buffer_utils import get_numpy_from_buffer_efficient, get_caps_from_pad
from hailo_apps.python.core.common.core import get_resource_path
from hailo_apps.python.core.common.defines import (
    RESOURCES_MODELS_DIR_NAME, RESOURCES_SO_DIR_NAME,
    RESOURCES_ROOT_PATH_DEFAULT,
    DETECTION_POSTPROCESS_SO_FILENAME, CLIP_POSTPROCESS_SO_FILENAME,
)
from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import (
    INFERENCE_PIPELINE, INFERENCE_PIPELINE_WRAPPER,
    TRACKER_PIPELINE, USER_CALLBACK_PIPELINE, CROPPER_PIPELINE,
)
from PIL import Image


def main():
    image_file = sys.argv[1]
    cat_name = sys.argv[2]
    database_dir = sys.argv[3]
    samples_dir = sys.argv[4]
    threshold = float(sys.argv[5])
    arch = sys.argv[6]

    os.makedirs(samples_dir, exist_ok=True)
    os.makedirs(database_dir, exist_ok=True)

    db = DatabaseHandler(
        db_name="cats.db", table_name="cats", schema=Record,
        threshold=threshold, database_dir=database_dir, samples_dir=samples_dir,
    )

    hef_detection = get_resource_path(None, RESOURCES_MODELS_DIR_NAME, arch, "yolov8m")
    hef_clip = get_resource_path(None, RESOURCES_MODELS_DIR_NAME, arch, "clip_vit_b_32_image_encoder")
    so_detection = get_resource_path(None, RESOURCES_SO_DIR_NAME, arch, DETECTION_POSTPROCESS_SO_FILENAME)
    so_clip = get_resource_path(None, RESOURCES_SO_DIR_NAME, arch, CLIP_POSTPROCESS_SO_FILENAME)
    so_cropper = os.path.join(
        RESOURCES_ROOT_PATH_DEFAULT, RESOURCES_SO_DIR_NAME,
        "liball_detections_cropper_postprocess.so",
    )

    Gst.init(None)

    source = (
        f"multifilesrc location={image_file} loop=true num-buffers=30 ! "
        f"decodebin ! videoconvert n-threads=4 qos=false ! "
        f"video/x-raw, format=RGB, pixel-aspect-ratio=1/1 "
    )
    detection = INFERENCE_PIPELINE(
        hef_path=hef_detection, post_process_so=so_detection,
        post_function_name="filter", batch_size=1,
        scheduler_priority=31, scheduler_timeout_ms=100,
        name="detection_inference", multi_process_service="true",
    )
    detection_wrapper = INFERENCE_PIPELINE_WRAPPER(detection)
    tracker = TRACKER_PIPELINE(class_id=-1, keep_past_metadata=True)
    clip_inf = INFERENCE_PIPELINE(
        hef_path=hef_clip, post_process_so=so_clip,
        post_function_name="filter", batch_size=1,
        scheduler_priority=16, scheduler_timeout_ms=1000,
        name="clip_inference", multi_process_service="true",
    )
    cropper = CROPPER_PIPELINE(
        inner_pipeline=clip_inf, so_path=so_cropper,
        function_name="all_detections", name="clip_cropper",
    )
    train_cb = USER_CALLBACK_PIPELINE(name="train_cb")

    pipeline_str = (
        f"{source} ! {detection_wrapper} ! {tracker} ! {cropper} ! "
        f"{train_cb} ! fakesink"
    )
    pipeline = Gst.parse_launch(pipeline_str)

    result = {"processed": False}

    def train_callback(pad, info, _user_data):
        if result["processed"]:
            return Gst.PadProbeReturn.OK
        buffer = info.get_buffer()
        if buffer is None:
            return Gst.PadProbeReturn.OK
        fmt, width, height = get_caps_from_pad(pad)
        frame = get_numpy_from_buffer_efficient(buffer, fmt, width, height)
        roi = hailo.get_roi_from_buffer(buffer)

        for det in roi.get_objects_typed(hailo.HAILO_DETECTION):
            if det.get_label() != "cat":
                continue
            matrices = det.get_objects_typed(hailo.HAILO_MATRIX)
            if len(matrices) != 1:
                continue
            embedding_vector = np.array(matrices[0].get_data())
            det.remove_object(matrices[0])

            bbox = det.get_bbox()
            x_min = max(0, int((bbox.xmin() - 0.15) * width))
            y_min = max(0, int((bbox.ymin() - 0.15) * height))
            x_max = min(width, int((bbox.xmax() + 0.15) * width))
            y_max = min(height, int((bbox.ymax() + 0.15) * height))
            crop = frame[y_min:y_max, x_min:x_max]
            sample_path = os.path.join(samples_dir, f"{uuid.uuid4()}.jpeg")
            Image.fromarray(crop).save(sample_path, format="JPEG", quality=85)

            existing = db.get_record_by_label(label=cat_name)
            if existing:
                db.insert_new_sample(
                    record=existing, embedding=embedding_vector,
                    sample=sample_path, timestamp=int(time.time()),
                )
                print(f"Added sample to {cat_name}")
            else:
                record = db.create_record(
                    embedding=embedding_vector, sample=sample_path,
                    timestamp=int(time.time()), label=cat_name,
                )
                print(f"New cat: {cat_name} (ID: {record['global_id']})")
            result["processed"] = True
            return Gst.PadProbeReturn.OK
        return Gst.PadProbeReturn.OK

    identity = pipeline.get_by_name("train_cb")
    if identity:
        pad = identity.get_static_pad("src")
        pad.add_probe(Gst.PadProbeType.BUFFER, train_callback, None)

    pipeline.set_state(Gst.State.PLAYING)
    time.sleep(5)
    pipeline.set_state(Gst.State.NULL)
    time.sleep(0.5)
    os._exit(0)  # Clean exit to avoid GStreamer cleanup segfault


if __name__ == "__main__":
    main()
