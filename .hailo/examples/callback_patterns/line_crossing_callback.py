"""
Callback Pattern: Line Crossing Detection

Demonstrates counting objects crossing a virtual horizontal line.
Uses tracker IDs to detect when an object's center crosses the line
between consecutive frames, with direction tracking (up/down).

This is an isolated example — adapt into your app's callback.
"""
import cv2
import hailo

from hailo_apps.python.core.common.buffer_utils import (
    get_caps_from_pad,
    get_numpy_from_buffer,
)
from hailo_apps.python.core.gstreamer.gstreamer_app import app_callback_class


class LineCrossingCallbackData(app_callback_class):
    """Callback state for line crossing counting."""
    def __init__(self, line_y=0.5, target_label="person"):
        super().__init__()
        self.line_y = line_y            # Normalized Y position [0,1]
        self.target_label = target_label
        self.prev_positions = {}        # {track_id: y_center}
        self.count_down = 0             # Crossed top -> bottom
        self.count_up = 0               # Crossed bottom -> top
        self.counted_ids = set()        # Avoid double-counting


def app_callback(element, buffer, user_data):
    """Detect objects crossing a virtual line."""
    if buffer is None:
        return

    frame_idx = user_data.get_count()
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    current_positions = {}

    for detection in detections:
        if detection.get_label() != user_data.target_label:
            continue

        # Get tracker ID
        track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
        if len(track) != 1:
            continue
        track_id = track[0].get_id()
        if track_id == 0:
            continue

        # Get center Y position (normalized)
        bbox = detection.get_bbox()
        y_center = bbox.ymin() + bbox.height() / 2.0
        current_positions[track_id] = y_center

    # Check for line crossings
    for track_id, y_center in current_positions.items():
        if track_id in user_data.counted_ids:
            continue  # Already counted this object

        if track_id in user_data.prev_positions:
            prev_y = user_data.prev_positions[track_id]

            # Crossed downward (top to bottom)
            if prev_y < user_data.line_y <= y_center:
                user_data.count_down += 1
                user_data.counted_ids.add(track_id)

            # Crossed upward (bottom to top)
            elif prev_y > user_data.line_y >= y_center:
                user_data.count_up += 1
                user_data.counted_ids.add(track_id)

    # Update positions for next frame
    user_data.prev_positions = current_positions

    # Clean up counted IDs for objects that left the frame
    user_data.counted_ids &= set(current_positions.keys())

    # Optional: draw line and counts on frame
    if user_data.use_frame:
        pad = element.get_static_pad("src")
        fmt, width, height = get_caps_from_pad(pad)
        if fmt and width and height:
            frame = get_numpy_from_buffer(buffer, fmt, width, height)
            line_y_px = int(user_data.line_y * height)

            # Draw the counting line
            cv2.line(frame, (0, line_y_px), (width, line_y_px), (0, 0, 255), 2)

            # Draw counts
            cv2.putText(
                frame, f"Down: {user_data.count_down}  Up: {user_data.count_up}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
            )

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            user_data.set_frame(frame)

    # Print summary periodically
    if frame_idx % 30 == 0:
        total = user_data.count_down + user_data.count_up
        print(
            f"Frame {frame_idx}: "
            f"Down={user_data.count_down} Up={user_data.count_up} Total={total}"
        )
