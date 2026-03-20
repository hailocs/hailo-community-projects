"""
Callback Pattern: Polygon Zone Counting

Demonstrates counting objects within defined polygon zones.
Zones are defined in normalized [0,1] coordinates and support
point-in-polygon tests for bbox centers.

This is an isolated example — adapt into your app's callback.
"""
import json

import cv2
import hailo
import numpy as np

from hailo_apps.python.core.common.buffer_utils import (
    get_caps_from_pad,
    get_numpy_from_buffer,
)
from hailo_apps.python.core.gstreamer.gstreamer_app import app_callback_class


class Zone:
    """A polygon region in normalized [0,1] coordinates."""

    def __init__(self, name, polygon, capacity=1):
        self.name = name
        self.polygon = np.array(polygon, dtype=np.float32)
        self.capacity = capacity
        self.occupied_count = 0

    def contains_point(self, x, y):
        """Ray-casting point-in-polygon test."""
        n = len(self.polygon)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = self.polygon[i]
            xj, yj = self.polygon[j]
            if ((yi > y) != (yj > y)) and \
               (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    def contains_bbox_center(self, bbox):
        """Check if a HailoBBox center falls in this zone."""
        cx = bbox.xmin() + bbox.width() / 2.0
        cy = bbox.ymin() + bbox.height() / 2.0
        return self.contains_point(cx, cy)


def get_default_zones():
    """Default 2x2 grid zones for demo."""
    return [
        Zone("Zone A", [[0, 0], [0.5, 0], [0.5, 0.5], [0, 0.5]], capacity=4),
        Zone("Zone B", [[0.5, 0], [1, 0], [1, 0.5], [0.5, 0.5]], capacity=4),
        Zone("Zone C", [[0, 0.5], [0.5, 0.5], [0.5, 1], [0, 1]], capacity=4),
        Zone("Zone D", [[0.5, 0.5], [1, 0.5], [1, 1], [0.5, 1]], capacity=4),
    ]


class ZoneCountingCallbackData(app_callback_class):
    """Callback state for zone-based counting."""
    def __init__(self, zones=None):
        super().__init__()
        self.zones = zones or get_default_zones()


def draw_zones_on_frame(frame, zones, width, height):
    """Draw zone polygons with occupancy status on frame."""
    for zone in zones:
        is_full = zone.occupied_count >= zone.capacity
        color = (0, 0, 255) if is_full else (0, 255, 0)

        pts = zone.polygon.copy()
        pts[:, 0] *= width
        pts[:, 1] *= height
        pts = pts.astype(np.int32)

        # Semi-transparent fill
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], color)
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

        # Border
        cv2.polylines(frame, [pts], True, color, 2)

        # Label
        cx = int(pts[:, 0].mean())
        cy = int(pts[:, 1].mean())
        cv2.putText(
            frame, f"{zone.name}: {zone.occupied_count}/{zone.capacity}",
            (cx - 50, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2
        )


def app_callback(element, buffer, user_data):
    """Count detections per zone and optionally draw zones on frame."""
    if buffer is None:
        return

    frame_idx = user_data.get_count()
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Reset zone counts for this frame
    for zone in user_data.zones:
        zone.occupied_count = 0

    # Count detections per zone
    for detection in detections:
        bbox = detection.get_bbox()
        for zone in user_data.zones:
            if zone.contains_bbox_center(bbox):
                zone.occupied_count += 1
                break  # Each detection counts in one zone only

    # Optional: draw zones on frame
    if user_data.use_frame:
        pad = element.get_static_pad("src")
        fmt, width, height = get_caps_from_pad(pad)
        if fmt and width and height:
            frame = get_numpy_from_buffer(buffer, fmt, width, height)
            draw_zones_on_frame(frame, user_data.zones, width, height)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            user_data.set_frame(frame)

    # Print summary periodically
    if frame_idx % 30 == 0:
        status = ", ".join(
            f"{z.name}={z.occupied_count}/{z.capacity}" for z in user_data.zones
        )
        print(f"Frame {frame_idx}: {status}")
