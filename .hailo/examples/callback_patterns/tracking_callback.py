"""
Callback Pattern: Per-Object Tracking with State Management

Demonstrates maintaining per-tracked-object state across frames.
Each tracked person gets their own state dict (first seen time, custom data).
Stale entries are cleaned up when objects leave the frame.

This is an isolated example — adapt into your app's callback.
"""
import hailo
from hailo_apps.python.core.gstreamer.gstreamer_app import app_callback_class


class TrackedObjectState:
    """State for a single tracked object."""
    def __init__(self, first_frame):
        self.first_frame = first_frame
        self.frames_seen = 0
        self.last_label = ""
        self.last_confidence = 0.0
        self.custom_data = {}


class TrackingCallbackData(app_callback_class):
    """Callback state with per-track-ID state management."""
    def __init__(self):
        super().__init__()
        self.track_states = {}  # {track_id: TrackedObjectState}

    def get_or_create(self, track_id):
        """Get existing state or create new one for a track ID."""
        if track_id not in self.track_states:
            self.track_states[track_id] = TrackedObjectState(
                first_frame=self.get_count()
            )
        return self.track_states[track_id]

    def cleanup_stale(self, active_ids, max_missing_frames=300):
        """Remove state for objects not seen recently."""
        current_frame = self.get_count()
        stale_ids = [
            tid for tid, state in self.track_states.items()
            if tid not in active_ids
            and (current_frame - state.first_frame) > max_missing_frames
        ]
        for tid in stale_ids:
            del self.track_states[tid]


def app_callback(element, buffer, user_data):
    """
    Track individual objects across frames.

    Each detected person with a unique tracker ID gets a persistent state
    object. You can store anything per-object: dwell time, trajectory,
    classification history, etc.
    """
    if buffer is None:
        return

    frame_idx = user_data.get_count()
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    active_ids = set()

    for detection in detections:
        label = detection.get_label()
        if label != "person":
            continue

        # Extract tracker ID
        track = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
        if len(track) != 1:
            continue
        track_id = track[0].get_id()
        if track_id == 0:
            continue  # Untracked detection

        active_ids.add(track_id)

        # Get or create per-object state
        state = user_data.get_or_create(track_id)
        state.frames_seen += 1
        state.last_label = label
        state.last_confidence = detection.get_confidence()

        # Example: track dwell time
        dwell_frames = frame_idx - state.first_frame
        state.custom_data["dwell_frames"] = dwell_frames

    # Clean up objects that left the frame
    user_data.cleanup_stale(active_ids)

    # Print summary periodically
    if frame_idx % 30 == 0:
        active_count = len(user_data.track_states)
        print(f"Frame {frame_idx}: Tracking {active_count} people")
        for tid, state in list(user_data.track_states.items())[:3]:
            dwell = state.custom_data.get("dwell_frames", 0)
            print(f"  ID {tid}: seen {state.frames_seen}x, dwell={dwell} frames")
