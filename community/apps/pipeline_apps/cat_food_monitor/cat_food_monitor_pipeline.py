# region imports
# Standard library imports
import os
import shutil
import json
import sys
import time
import threading
import queue
import uuid
import setproctitle
from pathlib import Path
os.environ["GST_PLUGIN_FEATURE_RANK"] = "vaapidecodebin:NONE"

# Third-party imports
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import numpy as np
from PIL import Image

# Local application-specific imports
import hailo
from hailo import HailoTracker
from hailo_apps.python.core.common.db_handler import DatabaseHandler, Record
from hailo_apps.python.core.common.core import (
    get_pipeline_parser,
    get_resource_path,
)
from hailo_apps.python.core.common.buffer_utils import get_numpy_from_buffer_efficient, get_caps_from_pad
from hailo_apps.python.core.gstreamer.gstreamer_app import GStreamerApp
from hailo_apps.python.core.common.defines import (
    RESOURCES_SO_DIR_NAME,
    RESOURCES_MODELS_DIR_NAME,
    DETECTION_POSTPROCESS_SO_FILENAME,
    CLIP_POSTPROCESS_SO_FILENAME,
    CLIP_POSTPROCESS_FUNCTION_NAME,
    CLIP_DETECTION_POSTPROCESS_FUNCTION_NAME,
    BASIC_PIPELINES_VIDEO_EXAMPLE_NAME,
    HAILO8_ARCH,
    HAILO8L_ARCH,
    FACE_RECON_DATABASE_DIR_NAME,
    FACE_RECON_SAMPLES_DIR_NAME,
    RESOURCES_ROOT_PATH_DEFAULT,
)
from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import (
    QUEUE,
    SOURCE_PIPELINE,
    INFERENCE_PIPELINE,
    INFERENCE_PIPELINE_WRAPPER,
    TRACKER_PIPELINE,
    USER_CALLBACK_PIPELINE,
    DISPLAY_PIPELINE,
    CROPPER_PIPELINE,
)
from hailo_apps.python.core.common.hailo_logger import get_logger

hailo_logger = get_logger(__name__)
# endregion imports

# Application title for process name
CAT_FOOD_MONITOR_APP_TITLE = "cat_food_monitor"

# Model names
DETECTION_MODEL_NAME = "yolov8m"
CLIP_IMAGE_ENCODER_MODEL_NAME = "clip_vit_b_32_image_encoder"

# Cat label in COCO dataset
CAT_LABEL = "cat"


class GStreamerCatFoodMonitorApp(GStreamerApp):
    def __init__(self, app_callback, user_data, parser=None):
        if parser is None:
            parser = get_pipeline_parser()
        parser.add_argument(
            "--mode", default='run',
            help="The mode of the application: run, train, delete"
        )

        super().__init__(parser, user_data)
        setproctitle.setproctitle(CAT_FOOD_MONITOR_APP_TITLE)

        # Load algorithm parameters
        json_file_path = os.path.join(os.path.dirname(__file__), "cat_food_algo_params.json")
        with open(json_file_path, "r") as json_file:
            self.algo_params = json.load(json_file)

        self.skip_frames = self.algo_params['skip_frames']
        self.lance_db_vector_search_classificaiton_confidence_threshold = (
            self.algo_params['lance_db_vector_search_classificaiton_confidence_threshold']
        )
        self.batch_size = self.algo_params.get('batch_size', 1)

        # Initialize directories
        current_dir = Path(__file__).parent
        self.train_images_dir = current_dir / "train"
        self.samples_dir = current_dir / FACE_RECON_SAMPLES_DIR_NAME
        self.database_dir = current_dir / FACE_RECON_DATABASE_DIR_NAME
        os.makedirs(self.train_images_dir, exist_ok=True)
        os.makedirs(self.samples_dir, exist_ok=True)

        # Initialize the database and table for cat embeddings (CLIP 512-dim)
        self.db_handler = DatabaseHandler(
            db_name='cats.db',
            table_name='cats',
            schema=Record,
            threshold=self.lance_db_vector_search_classificaiton_confidence_threshold,
            database_dir=self.database_dir,
            samples_dir=self.samples_dir,
        )

        self.current_file = None  # for train mode
        self.processed_names = set()
        self.processed_files = set()

        # Resolve HEF paths for detection (YOLOv8) and CLIP image encoder
        self.hef_path_detection = get_resource_path(
            pipeline_name=None,
            resource_type=RESOURCES_MODELS_DIR_NAME,
            arch=self.arch,
            model=DETECTION_MODEL_NAME,
        )
        self.hef_path_clip = get_resource_path(
            pipeline_name=None,
            resource_type=RESOURCES_MODELS_DIR_NAME,
            arch=self.arch,
            model=CLIP_IMAGE_ENCODER_MODEL_NAME,
        )

        # Postprocess shared objects
        self.post_process_so_detection = get_resource_path(
            pipeline_name=None,
            resource_type=RESOURCES_SO_DIR_NAME,
            arch=self.arch,
            model=DETECTION_POSTPROCESS_SO_FILENAME,
        )
        self.post_process_so_clip = get_resource_path(
            pipeline_name=None,
            resource_type=RESOURCES_SO_DIR_NAME,
            arch=self.arch,
            model=CLIP_POSTPROCESS_SO_FILENAME,
        )
        # Use the all-detections cropper (works with any detection model, unlike CLIP-specific croppers)
        self.post_process_so_cropper = os.path.join(
            RESOURCES_ROOT_PATH_DEFAULT, RESOURCES_SO_DIR_NAME,
            'liball_detections_cropper_postprocess.so',
        )

        # Postprocess function names
        self.detection_func = CLIP_DETECTION_POSTPROCESS_FUNCTION_NAME
        self.clip_func = CLIP_POSTPROCESS_FUNCTION_NAME
        self.cropper_func = 'all_detections'

        # Multi-process service for hailo8/hailo8l (requires hailort.service active)
        # Enabled for 'run' mode; disabled for 'train' mode to avoid pipeline recreation crashes
        if self.options_menu.mode == 'run':
            self.multi_process_service = (
                'true' if self.arch in (HAILO8_ARCH, HAILO8L_ARCH) else None
            )
        else:
            self.multi_process_service = None

        # Callbacks
        self.app_callback = app_callback
        self.vector_db_callback_name = "vector_db_callback"
        self.train_vector_db_callback_name = "train_vector_db_callback"
        self.track_id_frame_count = {}

        if self.options_menu.mode == 'run':
            self.create_pipeline()
            self.connect_vector_db_callback()
            self.tracker = HailoTracker.get_instance()
        # In train mode, pipeline is created per-image in run_training()

        # Worker queue thread for saving images
        self.task_queue = queue.Queue()

        def worker():
            while True:
                task = self.task_queue.get()
                if task is None:
                    break
                if task['type'] == 'save_image':
                    frame, image_path = task['frame'], task['image_path']
                    self.save_image_file(frame, image_path)
                self.task_queue.task_done()

        self.num_worker_threads = 1
        self.threads = []
        for _ in range(self.num_worker_threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

    def get_pipeline_string(self):
        source_pipeline = SOURCE_PIPELINE(
            self.video_source, self.video_width, self.video_height,
            frame_rate=self.frame_rate, sync=self.sync,
        )

        detection_pipeline = INFERENCE_PIPELINE(
            hef_path=self.hef_path_detection,
            post_process_so=self.post_process_so_detection,
            post_function_name=self.detection_func,
            batch_size=self.batch_size,
            scheduler_priority=31,
            scheduler_timeout_ms=100,
            name='detection_inference',
            multi_process_service=self.multi_process_service,
        )
        detection_pipeline_wrapper = INFERENCE_PIPELINE_WRAPPER(detection_pipeline)

        # Track all detections; filter to "cat" label in callbacks
        tracker_pipeline = TRACKER_PIPELINE(
            class_id=-1, kalman_dist_thr=0.7, iou_thr=0.8,
            init_iou_thr=0.9, keep_new_frames=2, keep_tracked_frames=6,
            keep_lost_frames=8, keep_past_metadata=True,
            name='hailo_cat_tracker',
        )

        clip_pipeline = INFERENCE_PIPELINE(
            hef_path=self.hef_path_clip,
            post_process_so=self.post_process_so_clip,
            post_function_name=self.clip_func,
            batch_size=self.batch_size,
            scheduler_priority=16,
            scheduler_timeout_ms=1000,
            name='clip_inference',
            multi_process_service=self.multi_process_service,
        )

        cropper_pipeline = CROPPER_PIPELINE(
            inner_pipeline=clip_pipeline,
            so_path=self.post_process_so_cropper,
            function_name=self.cropper_func,
            name='clip_cropper',
        )

        vector_db_callback_pipeline = USER_CALLBACK_PIPELINE(
            name=self.vector_db_callback_name,
        )
        user_callback_pipeline = USER_CALLBACK_PIPELINE()
        display_pipeline = DISPLAY_PIPELINE(
            video_sink=self.video_sink, sync=self.sync, show_fps=self.show_fps,
        )

        if self.options_menu.mode == 'train':
            source_pipeline = (
                f"multifilesrc location={self.current_file} loop=true num-buffers=30 ! "
                f"decodebin ! videoconvert n-threads=4 qos=false ! "
                f"video/x-raw, format=RGB, pixel-aspect-ratio=1/1 "
            )
            vector_db_callback_pipeline = USER_CALLBACK_PIPELINE(
                name=self.train_vector_db_callback_name,
            )

        return (
            f'{source_pipeline} ! '
            f'{detection_pipeline_wrapper} ! '
            f'{tracker_pipeline} ! '
            f'{cropper_pipeline} ! '
            f'{vector_db_callback_pipeline} ! '
            f'{user_callback_pipeline} ! '
            f'{display_pipeline}'
        )

    def run(self):
        if self.options_menu.mode == 'run':
            super().run()
        else:  # train
            self.run_training()

    def run_training(self):
        """
        Iterate over the training folder structured with subfolders (cat names),
        generate CLIP embeddings for each image, and store them in the database.
        Training folder structure: train/<cat_name>/<image_files>

        Uses a subprocess per cat to avoid GStreamer pipeline recreation segfaults
        with hailocropper/CLIP elements.
        """
        if not os.listdir(self.train_images_dir):
            print(
                f"Training directory {self.train_images_dir} is empty. "
                f"Please add cat images in subdirectories named after each cat."
            )
            print(f"Expected structure: {self.train_images_dir}/<cat_name>/<image_files>")
            sys.exit(1)

        print(f"Training on images from {self.train_images_dir}")
        for cat_name in sorted(os.listdir(self.train_images_dir)):
            cat_folder = os.path.join(self.train_images_dir, cat_name)
            if self.db_handler.get_record_by_label(label=cat_name):
                print(f"Cat '{cat_name}' already in database, skipping.")
                continue
            if not os.path.isdir(cat_folder):
                continue
            image_files = [
                os.path.join(cat_folder, f)
                for f in sorted(os.listdir(cat_folder))
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
            ]
            if not image_files:
                continue
            print(f"Processing cat: {cat_name} ({len(image_files)} images)")
            self._train_cat_subprocess(cat_name, image_files)
        print("Training completed")

    def _train_cat_subprocess(self, cat_name, image_files):
        """Train a single cat using a subprocess to avoid pipeline recreation issues."""
        import subprocess
        script = os.path.join(os.path.dirname(__file__), "_train_single_cat.py")
        # Write a temporary training script if it doesn't exist
        if not os.path.exists(script):
            self._create_train_helper_script(script)

        for image_file in image_files:
            print(f"  Processing: {os.path.basename(image_file)}", flush=True)
            result = subprocess.run(
                [sys.executable, script, image_file, cat_name,
                 str(self.database_dir), str(self.samples_dir),
                 str(self.lance_db_vector_search_classificaiton_confidence_threshold),
                 self.arch],
                capture_output=True, text=True, timeout=60,
            )
            if result.stdout.strip():
                print(f"    {result.stdout.strip()}")
            if result.returncode != 0:
                stderr = result.stderr.strip().split('\n')[-3:] if result.stderr else []
                print(f"    Warning: exit code {result.returncode}")
                for line in stderr:
                    if line.strip():
                        print(f"    {line.strip()}")

    def _create_train_helper_script(self, script_path):
        """Create the single-image training helper script."""
        content = '''#!/usr/bin/env python3
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
'''
        with open(script_path, 'w') as f:
            f.write(content)

    def connect_vector_db_callback(self):
        identity = self.pipeline.get_by_name(self.vector_db_callback_name)
        if identity:
            identity_pad = identity.get_static_pad("src")
            identity_pad.add_probe(
                Gst.PadProbeType.BUFFER, self.vector_db_callback, self.user_data,
            )

    def connect_train_vector_db_callback(self):
        identity = self.pipeline.get_by_name(self.train_vector_db_callback_name)
        if identity:
            identity_pad = identity.get_static_pad("src")
            identity_pad.add_probe(
                Gst.PadProbeType.BUFFER, self.train_vector_db_callback, self.user_data,
            )

    def save_image_file(self, frame, image_path):
        image = Image.fromarray(frame)
        image.save(image_path, format="JPEG", quality=85)

    def crop_frame(self, frame, bbox, width, height):
        x_min = max(0, min(bbox.xmin() - 0.15, 1))
        y_min = max(0, min(bbox.ymin() - 0.15, 1))
        x_max = max(0, min(bbox.xmax() + 0.15, 1))
        y_max = max(0, min(bbox.ymax() + 0.15, 1))
        x_min = int(x_min * width)
        y_min = int(y_min * height)
        x_max = int(x_max * width)
        y_max = int(y_max * height)
        return frame[y_min:y_max, x_min:x_max]

    def add_task(self, task_type, **kwargs):
        task = {'type': task_type, **kwargs}
        self.task_queue.put(task)

    def get_processed_names_by_name(self, key):
        for k, v in self.processed_names:
            if k == key:
                return v
        return None

    def is_name_processed(self, key):
        for k, _ in self.processed_names:
            if k == key:
                return True
        return False

    def vector_db_callback(self, pad, info, user_data):
        """
        Runtime callback: for each detected cat with a CLIP embedding,
        search the vector DB and add classification metadata with the cat's name.
        """
        tracker_name = self.tracker.get_trackers_list()[0]
        buffer = info.get_buffer()
        if buffer is None:
            return Gst.PadProbeReturn.OK
        format, width, height = get_caps_from_pad(pad)
        roi = hailo.get_roi_from_buffer(buffer)

        for detection in roi.get_objects_typed(hailo.HAILO_DETECTION):
            # Filter to cat detections only
            if detection.get_label() != CAT_LABEL:
                continue

            track_id = (
                detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)[0].get_id()
                if detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
                else None
            )

            if self.track_id_frame_count.get(track_id, 0) < self.skip_frames:
                self.track_id_frame_count[track_id] = (
                    self.track_id_frame_count.get(track_id, 0) + 1
                )
                continue

            # Extract CLIP embedding from the detection
            embedding = detection.get_objects_typed(hailo.HAILO_MATRIX)
            if len(embedding) == 0:
                continue
            if len(embedding) > 1:
                detection.remove_object(embedding[0])
                continue

            embedding_vector = np.array(embedding[0].get_data())
            cat_record = self.db_handler.search_record(embedding=embedding_vector)
            new_confidence = 1 - cat_record['_distance']
            classification = detection.get_objects_typed(hailo.HAILO_CLASSIFICATION)
            if not classification or classification[0].get_confidence() < new_confidence:
                if classification:
                    detection.remove_object(classification[0])
                new_classification = hailo.HailoClassification(
                    type='cat_recon',
                    label=cat_record['label'],
                    confidence=new_confidence,
                )
                detection.add_object(new_classification)
                if track_id is not None:
                    self.tracker.remove_classifications_from_track(
                        tracker_name, track_id, 'cat_recon',
                    )
                    self.tracker.add_object_to_track(
                        tracker_name, track_id, new_classification,
                    )

            # Re-process after skip_frames * 3 for periodic re-verification
            self.track_id_frame_count[track_id] = -3 * self.skip_frames

        return Gst.PadProbeReturn.OK

    def train_vector_db_callback(self, pad, info, user_data):
        """
        Training callback: extract CLIP embedding from detected cat and store in vector DB.
        """
        if self.current_file in self.processed_files:
            return Gst.PadProbeReturn.OK
        buffer = info.get_buffer()
        if buffer is None:
            return Gst.PadProbeReturn.OK
        format, width, height = get_caps_from_pad(pad)
        frame = get_numpy_from_buffer_efficient(buffer, format, width, height)
        roi = hailo.get_roi_from_buffer(buffer)

        detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
        if len(detections) == 0:
            print("No detections found in the current frame.")
            return Gst.PadProbeReturn.OK

        # Look for cat detections; if none found, try any detection with CLIP embedding
        cat_detections = [d for d in detections if d.get_label() == CAT_LABEL]
        if not cat_detections:
            # Fall back to any detection with a CLIP embedding (in case label mapping differs)
            cat_detections = [
                d for d in detections
                if len(d.get_objects_typed(hailo.HAILO_MATRIX)) > 0
            ]
            if cat_detections:
                print(
                    f"No '{CAT_LABEL}' detections found, using detection with label "
                    f"'{cat_detections[0].get_label()}' that has CLIP embedding."
                )
            else:
                print(f"No detections with CLIP embeddings found in frame.")
                return Gst.PadProbeReturn.OK

        for detection in cat_detections:
            embedding = detection.get_objects_typed(hailo.HAILO_MATRIX)
            if len(embedding) != 1:
                continue
            detection.remove_object(embedding[0])
            cropped_frame = self.crop_frame(frame, detection.get_bbox(), width, height)
            embedding_vector = np.array(embedding[0].get_data())
            image_path = os.path.join(self.samples_dir, f"{uuid.uuid4()}.jpeg")
            self.add_task('save_image', frame=cropped_frame, image_path=image_path)
            name = os.path.basename(os.path.dirname(self.current_file))
            if self.is_name_processed(name):
                self.db_handler.insert_new_sample(
                    record=self.db_handler.get_record_by_id(
                        self.get_processed_names_by_name(name),
                    ),
                    embedding=embedding_vector,
                    sample=image_path,
                    timestamp=int(time.time()),
                )
                print(f"Adding sample to cat: {name}")
            else:
                cat_record = self.db_handler.create_record(
                    embedding=embedding_vector,
                    sample=image_path,
                    timestamp=int(time.time()),
                    label=name,
                )
                print(f"New cat added with ID: {cat_record['global_id']}")
                self.processed_names.add((name, cat_record['global_id']))
            self.processed_files.add(self.current_file)
            return Gst.PadProbeReturn.OK
        return Gst.PadProbeReturn.OK
