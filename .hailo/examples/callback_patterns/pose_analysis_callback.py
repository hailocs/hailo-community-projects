"""
Callback Pattern: Pose Keypoint Extraction and Joint Angle Calculation

Demonstrates extracting COCO pose keypoints from YOLOv8-pose detections,
converting to pixel coordinates, and calculating joint angles. Useful for
exercise tracking, posture analysis, gesture recognition.

This is an isolated example — adapt into your app's callback.
"""
import math

import hailo
from hailo_apps.python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.python.core.common.buffer_utils import get_caps_from_pad

# COCO keypoint indices (17 keypoints)
KEYPOINTS = {
    "nose": 0,
    "left_eye": 1,     "right_eye": 2,
    "left_ear": 3,     "right_ear": 4,
    "left_shoulder": 5, "right_shoulder": 6,
    "left_elbow": 7,   "right_elbow": 8,
    "left_wrist": 9,   "right_wrist": 10,
    "left_hip": 11,    "right_hip": 12,
    "left_knee": 13,   "right_knee": 14,
    "left_ankle": 15,  "right_ankle": 16,
}


def get_keypoint_pixel(points, name, bbox, width, height):
    """
    Extract pixel coordinates for a named keypoint.

    Args:
        points: Landmark points from hailo (landmarks[0].get_points())
        name: Key from KEYPOINTS dict (e.g., "left_shoulder")
        bbox: HailoBBox from detection.get_bbox()
        width: Frame width in pixels
        height: Frame height in pixels

    Returns:
        (x, y) pixel tuple, or None if unavailable.
    """
    idx = KEYPOINTS.get(name)
    if idx is None or idx >= len(points):
        return None
    point = points[idx]
    x = (point.x() * bbox.width() + bbox.xmin()) * width
    y = (point.y() * bbox.height() + bbox.ymin()) * height
    return (x, y)


def calculate_angle(p1, p2, p3):
    """
    Calculate the angle at p2 formed by segments p1-p2 and p2-p3.

    Args:
        p1, p2, p3: (x, y) tuples. p2 is the vertex (the joint).

    Returns:
        Angle in degrees (0-180).
    """
    v1 = (p1[0] - p2[0], p1[1] - p2[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])

    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    if mag1 == 0 or mag2 == 0:
        return 0.0

    cos_angle = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cos_angle))


class PoseAnalysisCallbackData(app_callback_class):
    """Callback state for pose analysis."""
    def __init__(self):
        super().__init__()
        self.per_person_angles = {}  # {track_id: {"left_elbow": angle, ...}}


def app_callback(element, buffer, user_data):
    """
    Extract pose keypoints and calculate joint angles for each person.
    """
    if buffer is None:
        return

    frame_idx = user_data.get_count()

    # Get frame dimensions
    pad = element.get_static_pad("src")
    fmt, width, height = get_caps_from_pad(pad)
    if width is None or height is None:
        return

    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    for detection in detections:
        # Get tracker ID
        track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
        track_id = track[0].get_id() if len(track) == 1 else 0

        # Get landmarks (pose keypoints)
        landmarks = detection.get_objects_typed(hailo.HAILO_LANDMARKS)
        if not landmarks:
            continue

        points = landmarks[0].get_points()
        bbox = detection.get_bbox()

        # Extract specific keypoints as pixel coordinates
        left_shoulder = get_keypoint_pixel(points, "left_shoulder", bbox, width, height)
        left_elbow = get_keypoint_pixel(points, "left_elbow", bbox, width, height)
        left_wrist = get_keypoint_pixel(points, "left_wrist", bbox, width, height)
        left_hip = get_keypoint_pixel(points, "left_hip", bbox, width, height)
        left_knee = get_keypoint_pixel(points, "left_knee", bbox, width, height)
        left_ankle = get_keypoint_pixel(points, "left_ankle", bbox, width, height)

        angles = {}

        # Calculate left elbow angle (shoulder-elbow-wrist)
        if left_shoulder and left_elbow and left_wrist:
            angles["left_elbow"] = calculate_angle(
                left_shoulder, left_elbow, left_wrist
            )

        # Calculate left knee angle (hip-knee-ankle)
        if left_hip and left_knee and left_ankle:
            angles["left_knee"] = calculate_angle(
                left_hip, left_knee, left_ankle
            )

        # Calculate left shoulder angle (elbow-shoulder-hip)
        if left_elbow and left_shoulder and left_hip:
            angles["left_shoulder"] = calculate_angle(
                left_elbow, left_shoulder, left_hip
            )

        # Store angles per person
        if track_id > 0:
            user_data.per_person_angles[track_id] = angles

    # Print summary periodically
    if frame_idx % 30 == 0:
        for tid, angles in list(user_data.per_person_angles.items())[:3]:
            angle_str = ", ".join(f"{k}={v:.0f}" for k, v in angles.items())
            print(f"Frame {frame_idx} | Person {tid}: {angle_str}")
