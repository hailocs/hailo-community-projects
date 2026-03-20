#!/usr/bin/env python3
"""
Minimal Standalone Detection App

Simplest possible standalone HailoRT detection app using the 3-thread
architecture: preprocess -> infer -> visualize.

Usage:
    source setup_env.sh
    python standalone_example.py --input video.mp4
    python standalone_example.py --input usb --show-fps
    python standalone_example.py --input images/ --save-output --output-dir results/
"""
import os
import sys
import queue
import threading
import collections
from functools import partial
from pathlib import Path

import cv2
import numpy as np

# Handle both package and direct execution
try:
    from hailo_apps.python.core.common.hailo_inference import HailoInfer
    from hailo_apps.python.core.common.toolbox import (
        init_input_source,
        get_labels,
        load_json_file,
        preprocess,
        visualize,
        select_cap_processing_mode,
        FrameRateTracker,
    )
    from hailo_apps.python.core.common.defines import (
        MAX_INPUT_QUEUE_SIZE,
        MAX_OUTPUT_QUEUE_SIZE,
        MAX_ASYNC_INFER_JOBS,
    )
    from hailo_apps.python.core.common.parser import get_standalone_parser
    from hailo_apps.python.core.common.hailo_logger import get_logger, init_logging, level_from_args
    from hailo_apps.python.core.common.core import handle_and_resolve_args
except ImportError:
    repo_root = None
    for p in Path(__file__).resolve().parents:
        if (p / "hailo_apps" / "config" / "config_manager.py").exists():
            repo_root = p
            break
    if repo_root is not None:
        sys.path.insert(0, str(repo_root))
    from hailo_apps.python.core.common.hailo_inference import HailoInfer
    from hailo_apps.python.core.common.toolbox import (
        init_input_source, get_labels, load_json_file,
        preprocess, visualize, select_cap_processing_mode, FrameRateTracker,
    )
    from hailo_apps.python.core.common.defines import (
        MAX_INPUT_QUEUE_SIZE, MAX_OUTPUT_QUEUE_SIZE, MAX_ASYNC_INFER_JOBS,
    )
    from hailo_apps.python.core.common.parser import get_standalone_parser
    from hailo_apps.python.core.common.hailo_logger import get_logger, init_logging, level_from_args
    from hailo_apps.python.core.common.core import handle_and_resolve_args


APP_NAME = Path(__file__).stem
logger = get_logger(__name__)


def inference_result_handler(frame, result, labels, **kwargs):
    """Minimal postprocess: draw detections on frame."""
    # This is a placeholder -- real apps decode model-specific output format.
    # See hailo_apps/python/standalone_apps/object_detection/ for a full example.
    h, w = frame.shape[:2]
    cv2.putText(
        frame, f"Detections: {type(result).__name__}",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
    )
    return frame


def inference_callback(completion_info, bindings_list, input_batch, output_queue):
    """Called when async inference completes."""
    if completion_info.exception:
        logger.error(f"Inference error: {completion_info.exception}")
    else:
        for i, bindings in enumerate(bindings_list):
            if len(bindings._output_names) == 1:
                result = bindings.output().get_buffer()
            else:
                result = {
                    name: np.expand_dims(bindings.output(name).get_buffer(), axis=0)
                    for name in bindings._output_names
                }
            output_queue.put((input_batch[i], result))


def infer(hailo_inference, input_queue, output_queue, stop_event):
    """Inference thread: pulls batches, runs async inference, pushes results."""
    pending_jobs = collections.deque()

    while True:
        next_batch = input_queue.get()
        if not next_batch:
            break
        if stop_event.is_set():
            continue

        input_batch, preprocessed_batch = next_batch
        callback_fn = partial(
            inference_callback,
            input_batch=input_batch,
            output_queue=output_queue,
        )

        while len(pending_jobs) >= MAX_ASYNC_INFER_JOBS:
            pending_jobs.popleft().wait(10000)

        job = hailo_inference.run(preprocessed_batch, callback_fn)
        pending_jobs.append(job)

    hailo_inference.close()
    output_queue.put(None)


def parse_args():
    parser = get_standalone_parser()
    parser.description = "Minimal standalone detection example"
    parser.add_argument("--labels", "-l", type=str, default=None,
                        help="Path to labels text file")
    return parser.parse_args()


def main():
    args = parse_args()
    init_logging(level=level_from_args(args))
    handle_and_resolve_args(args, APP_NAME)

    labels = get_labels(args.labels)
    cap, images, input_type = init_input_source(args.input, args.batch_size, "sd")
    cap_processing_mode = None
    if cap is not None:
        cap_processing_mode = select_cap_processing_mode(
            input_type, args.save_output, args.frame_rate
        )

    stop_event = threading.Event()
    fps_tracker = FrameRateTracker() if args.show_fps else None

    input_q = queue.Queue(MAX_INPUT_QUEUE_SIZE)
    output_q = queue.Queue(MAX_OUTPUT_QUEUE_SIZE)

    post_fn = partial(inference_result_handler, labels=labels)
    hailo_inference = HailoInfer(args.hef_path, args.batch_size)
    height, width, _ = hailo_inference.get_input_shape()

    preprocess_t = threading.Thread(
        target=preprocess,
        args=(images, cap, args.frame_rate, args.batch_size, input_q,
              width, height, cap_processing_mode, None, stop_event),
    )
    postprocess_t = threading.Thread(
        target=visualize,
        args=(output_q, cap, args.save_output, args.output_dir,
              post_fn, fps_tracker, args.output_resolution,
              args.frame_rate, False, stop_event, args.no_display),
    )
    infer_t = threading.Thread(
        target=infer, args=(hailo_inference, input_q, output_q, stop_event)
    )

    preprocess_t.start()
    postprocess_t.start()
    infer_t.start()
    if fps_tracker:
        fps_tracker.start()

    try:
        preprocess_t.join()
        infer_t.join()
        postprocess_t.join()
    except KeyboardInterrupt:
        logger.info("Interrupted. Shutting down...")
        stop_event.set()
    finally:
        if fps_tracker:
            logger.info(fps_tracker.frame_rate_summary())
        logger.info("Processing completed.")


if __name__ == "__main__":
    main()
