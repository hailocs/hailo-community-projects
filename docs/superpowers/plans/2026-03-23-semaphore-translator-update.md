# Semaphore Translator Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the semaphore alphabet mapping to match the international maritime standard, add image source support to SOURCE_PIPELINE, and add tests.

**Architecture:** Three independent changes: (1) replace the SEMAPHORE_ALPHABET dict with corrected standard values, (2) add "image" source type to the GStreamer helper using multifilesrc, (3) add unit tests for the mapping logic and integration tests using real Hailo inference on reference images.

**Tech Stack:** Python, GStreamer (multifilesrc, decodebin), pytest, Hailo SDK

**Spec:** `docs/superpowers/specs/2026-03-22-semaphore-translator-update-design.md`

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `hailo-apps-infra/hailo_apps/python/core/gstreamer/gstreamer_helper_pipelines.py` | Modify | Add `"image"` source type to `get_source_type()` and `SOURCE_PIPELINE()` |
| `community/apps/pipeline_apps/semaphore_translator/semaphore_translator.py` | Modify | Replace `SEMAPHORE_ALPHABET` dict, fix angle convention comments, fix `decode_semaphore()` to use closest match |
| `tests/test_semaphore_translator.py` | Create | Unit tests (no hardware) + integration tests (`@pytest.mark.hailo`) |

---

### Task 1: Add image source type to SOURCE_PIPELINE

**Files:**
- Modify: `hailo-apps-infra/hailo_apps/python/core/gstreamer/gstreamer_helper_pipelines.py:40-55` (`get_source_type`) and `:89-185` (`SOURCE_PIPELINE`)

- [ ] **Step 1: Add `"image"` detection to `get_source_type()`**

In `hailo-apps-infra/hailo_apps/python/core/gstreamer/gstreamer_helper_pipelines.py`, add a new `elif` branch in `get_source_type()` **before** the final `else` (which returns `"file"`):

```python
def get_source_type(input_source):
    input_source = str(input_source)
    if input_source.startswith("/dev/video"):
        return "usb"
    elif input_source.startswith("rpi"):
        return "rpi"
    elif input_source.startswith("libcamera"):
        return "libcamera"
    elif input_source.startswith("0x"):
        return "ximage"
    elif input_source.startswith('rtsp://'):
        return 'rtsp'
    elif input_source.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
        return "image"
    else:
        return "file"
```

- [ ] **Step 2: Add `num_buffers` parameter and `"image"` branch to `SOURCE_PIPELINE()`**

Add `num_buffers=30` parameter to the `SOURCE_PIPELINE` function signature:

```python
def SOURCE_PIPELINE(
    video_source,
    video_width=640,
    video_height=640,
    name="source",
    no_webcam_compression=False,
    frame_rate=30,
    sync=True,
    video_format="RGB",
    mirror_image=True,
    num_buffers=30,
):
```

Add the `"image"` branch after the `"rtsp"` branch and before the `else` (file) branch:

```python
    elif source_type == "image":
        source_element = (
            f'multifilesrc location="{video_source}" loop=true num-buffers={num_buffers} ! '
            f'decodebin name={name}_decodebin ! '
        )
```

- [ ] **Step 3: Smoke test the change**

Run a quick syntax check:

```bash
cd /home/giladn/tappas_apps/repos/hailo-community-projects
python -c "from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import get_source_type, SOURCE_PIPELINE; print(get_source_type('test.jpg')); print(get_source_type('test.mp4'))"
```

Expected output:
```
image
file
```

- [ ] **Step 4: Commit (submodule + outer repo pointer)**

```bash
git -C hailo-apps-infra add hailo_apps/python/core/gstreamer/gstreamer_helper_pipelines.py
git -C hailo-apps-infra commit -m "feat: add image source type to SOURCE_PIPELINE using multifilesrc"
git add hailo-apps-infra
git commit -m "chore: update hailo-apps-infra submodule (image source type)"
```

---

### Task 2: Fix SEMAPHORE_ALPHABET mapping and decode_semaphore bug

**Files:**
- Modify: `community/apps/pipeline_apps/semaphore_translator/semaphore_translator.py:54-100` (alphabet) and `:138-156` (decode function)

- [ ] **Step 1: Replace the angle convention comments and SEMAPHORE_ALPHABET dict**

In `community/apps/pipeline_apps/semaphore_translator/semaphore_translator.py`, replace lines 54-100 (the comment block and the entire `SEMAPHORE_ALPHABET` dict) with:

```python
# Semaphore flag alphabet mapping (International Maritime Standard)
# Each letter is defined by the angles of the right and left arms.
# Angles are from the SIGNALER'S perspective, measured clockwise from straight down:
#   0° = down, 45° = down-right, 90° = right (horizontal), 135° = up-right,
#   180° = up, 225° = up-left, 270° = left (horizontal), 315° = down-left
#
# Note: compute_arm_angle() produces signaler-perspective angles directly
# because atan2(-dx, dy) on COCO keypoints (person's own left/right) mirrors
# the image coordinates back to the signaler's frame of reference.
#
# Format: (right_arm_angle, left_arm_angle)
# Angles are discretized to nearest 45-degree increment.
#
# References:
#   https://www.anbg.gov.au/flags/semaphore.html
#   https://en.wikipedia.org/wiki/Flag_semaphore
SEMAPHORE_ALPHABET = {
    # Circle 1 (A-G): one arm at 0° (down)
    (45, 0): "A",      # right low-right, left down
    (90, 0): "B",      # right horizontal-right, left down
    (135, 0): "C",     # right up-right, left down
    (180, 0): "D",     # right up, left down
    (0, 225): "E",     # right down, left up-left
    (0, 270): "F",     # right down, left horizontal-left
    (0, 315): "G",     # right down, left down-left
    # Circle 2 (H-N): one arm at 45°
    (90, 45): "H",     # right horizontal-right, left crosses to low-right
    (135, 45): "I",    # right up-right, left crosses to low-right
    (180, 270): "J",   # right up, left horizontal-left (also "letters follow")
    (45, 180): "K",    # right low-right, left up
    (45, 225): "L",    # right low-right, left up-left
    (45, 270): "M",    # right low-right, left horizontal-left
    (45, 315): "N",    # right low-right, left down-left
    # Circle 3 (O-S): one arm at 90°
    (90, 135): "O",    # right horizontal-right, left crosses to up-right
    (90, 180): "P",    # right horizontal-right, left up
    (90, 225): "Q",    # right horizontal-right, left up-left
    (90, 270): "R",    # right horizontal-right, left horizontal-left
    (90, 315): "S",    # right horizontal-right, left down-left
    # Circle 4 (T-U): one arm at 135°
    (135, 180): "T",   # right up-right, left up
    (135, 225): "U",   # right up-right, left up-left
    # Remaining letters
    (180, 315): "V",   # right up, left down-left
    (225, 270): "W",   # right crosses to up-left, left horizontal-left
    (225, 315): "X",   # right crosses to up-left, left down-left
    (135, 270): "Y",   # right up-right, left horizontal-left
    (315, 270): "Z",   # right crosses to down-left, left horizontal-left
    # Special signals
    (0, 0): "REST",
}
```

- [ ] **Step 2: Fix `decode_semaphore()` to return closest match instead of first match**

The current implementation does a linear scan and returns the **first** entry within `ANGLE_TOLERANCE`. With 45° spacing between positions and 30° tolerance, multiple letters can match off-center angles, causing incorrect results. Fix by finding the **closest** match (minimum combined angular distance).

In `community/apps/pipeline_apps/semaphore_translator/semaphore_translator.py`, replace the `decode_semaphore` function (lines 138-156) with:

```python
def decode_semaphore(right_arm_angle, left_arm_angle):
    """
    Given discretized arm angles, look up the semaphore letter.
    Returns the letter or '?' if no match found.
    Uses closest match within ANGLE_TOLERANCE for robustness.
    """
    key = (right_arm_angle, left_arm_angle)
    if key in SEMAPHORE_ALPHABET:
        return SEMAPHORE_ALPHABET[key]

    # Find closest match within tolerance
    best_letter = "?"
    best_distance = float("inf")
    for (r_angle, l_angle), letter in SEMAPHORE_ALPHABET.items():
        r_diff = abs(right_arm_angle - r_angle) % 360
        r_diff = min(r_diff, 360 - r_diff)
        l_diff = abs(left_arm_angle - l_angle) % 360
        l_diff = min(l_diff, 360 - l_diff)
        if r_diff <= ANGLE_TOLERANCE and l_diff <= ANGLE_TOLERANCE:
            distance = r_diff + l_diff
            if distance < best_distance:
                best_distance = distance
                best_letter = letter

    return best_letter
```

- [ ] **Step 3: Verify the module still imports cleanly**

```bash
cd /home/giladn/tappas_apps/repos/hailo-community-projects
python -c "from community.apps.pipeline_apps.semaphore_translator.semaphore_translator import SEMAPHORE_ALPHABET, decode_semaphore; print(f'{len(SEMAPHORE_ALPHABET)} entries'); print(decode_semaphore(90, 270))"
```

Expected output:
```
27 entries
R
```

- [ ] **Step 4: Commit**

```bash
git add community/apps/pipeline_apps/semaphore_translator/semaphore_translator.py
git commit -m "fix: align SEMAPHORE_ALPHABET with standard, fix decode closest-match bug"
```

---

### Task 3: Write unit tests for angle computation

**Files:**
- Create: `tests/test_semaphore_translator.py`

- [ ] **Step 1: Create test file with compute_arm_angle tests**

Create `tests/test_semaphore_translator.py`:

```python
"""Tests for the semaphore translator app.

Unit tests validate the angle computation and semaphore decoding logic
without requiring Hailo hardware. Integration tests (marked @pytest.mark.hailo)
run the full pipeline on reference images.
"""

import math
import os
import subprocess
import urllib.request
from pathlib import Path

import pytest

from community.apps.pipeline_apps.semaphore_translator.semaphore_translator import (
    compute_arm_angle,
    discretize_angle,
    decode_semaphore,
    SEMAPHORE_ALPHABET,
)


class TestComputeArmAngle:
    """Test compute_arm_angle() with known shoulder/wrist coordinates.

    The function computes angles from the signaler's perspective:
    0°=down, 90°=signaler's right, 180°=up, 270°=signaler's left.
    """

    @pytest.mark.parametrize(
        "dx,dy,expected_angle",
        [
            (0, 100, 0),       # straight down
            (-70, 70, 45),     # down-right (signaler's right, image-left)
            (-100, 0, 90),     # right (signaler's right, image-left)
            (-70, -70, 135),   # up-right (signaler's)
            (0, -100, 180),    # straight up
            (70, -70, 225),    # up-left (signaler's)
            (100, 0, 270),     # left (signaler's left, image-right)
            (70, 70, 315),     # down-left (signaler's)
        ],
        ids=["down", "down-right", "right", "up-right", "up", "up-left", "left", "down-left"],
    )
    def test_cardinal_directions(self, dx, dy, expected_angle):
        # Place shoulder at (200, 200), wrist offset by (dx, dy)
        shoulder_x, shoulder_y = 200, 200
        wrist_x = shoulder_x + dx
        wrist_y = shoulder_y + dy
        angle = compute_arm_angle(shoulder_x, shoulder_y, wrist_x, wrist_y)
        assert abs(angle - expected_angle) < 1.0, (
            f"Expected ~{expected_angle}°, got {angle:.1f}° for dx={dx}, dy={dy}"
        )
```

- [ ] **Step 2: Run test to verify it passes**

```bash
cd /home/giladn/tappas_apps/repos/hailo-community-projects
python -m pytest tests/test_semaphore_translator.py::TestComputeArmAngle -v
```

Expected: All 8 parametrized cases PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_semaphore_translator.py
git commit -m "test: add unit tests for compute_arm_angle"
```

---

### Task 4: Write unit tests for discretize_angle

**Files:**
- Modify: `tests/test_semaphore_translator.py`

- [ ] **Step 1: Add discretize_angle tests**

Append to `tests/test_semaphore_translator.py`:

```python
class TestDiscretizeAngle:
    """Test discretize_angle() snaps to nearest 45° increment."""

    @pytest.mark.parametrize(
        "input_angle,expected",
        [
            (0, 0),
            (22, 0),       # below midpoint → rounds down
            (23, 45),      # above midpoint → rounds up
            (44, 45),
            (45, 45),
            (90, 90),
            (112, 90),
            (113, 135),
            (180, 180),
            (270, 270),
            (315, 315),
            (337, 315),
            (338, 0),      # wraps around to 0
            (359, 0),
        ],
    )
    def test_snapping(self, input_angle, expected):
        result = discretize_angle(input_angle)
        assert result == expected, f"discretize_angle({input_angle}) = {result}, expected {expected}"
```

- [ ] **Step 2: Run test to verify it passes**

```bash
python -m pytest tests/test_semaphore_translator.py::TestDiscretizeAngle -v
```

Expected: All 14 parametrized cases PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_semaphore_translator.py
git commit -m "test: add unit tests for discretize_angle"
```

---

### Task 5: Write unit tests for decode_semaphore (all letters)

**Files:**
- Modify: `tests/test_semaphore_translator.py`

- [ ] **Step 1: Add decode_semaphore tests for all 26 letters + REST**

Append to `tests/test_semaphore_translator.py`:

```python
# The complete standard mapping for test assertions
STANDARD_SEMAPHORE = {
    "A": (45, 0),
    "B": (90, 0),
    "C": (135, 0),
    "D": (180, 0),
    "E": (0, 225),
    "F": (0, 270),
    "G": (0, 315),
    "H": (90, 45),
    "I": (135, 45),
    "J": (180, 270),
    "K": (45, 180),
    "L": (45, 225),
    "M": (45, 270),
    "N": (45, 315),
    "O": (90, 135),
    "P": (90, 180),
    "Q": (90, 225),
    "R": (90, 270),
    "S": (90, 315),
    "T": (135, 180),
    "U": (135, 225),
    "V": (180, 315),
    "W": (225, 270),
    "X": (225, 315),
    "Y": (135, 270),
    "Z": (315, 270),
    "REST": (0, 0),
}


class TestDecodeSemaphore:
    """Test decode_semaphore() against all standard letters."""

    @pytest.mark.parametrize(
        "letter",
        list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["REST"],
    )
    def test_exact_angles(self, letter):
        right_angle, left_angle = STANDARD_SEMAPHORE[letter]
        result = decode_semaphore(right_angle, left_angle)
        assert result == letter, (
            f"decode_semaphore({right_angle}, {left_angle}) = '{result}', expected '{letter}'"
        )

    def test_no_duplicate_position_pairs(self):
        """Verify all 26 letters use unique unordered position pairs."""
        pairs = set()
        for (r, l), letter in SEMAPHORE_ALPHABET.items():
            if letter == "REST":
                continue
            pair = frozenset([r, l])
            assert pair not in pairs, f"Duplicate position pair {pair} for letter '{letter}'"
            pairs.add(pair)
        assert len(pairs) == 26

    @pytest.mark.parametrize(
        "letter",
        list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    )
    def test_tolerance(self, letter):
        """Angles within ANGLE_TOLERANCE (30°) should still decode correctly."""
        right_angle, left_angle = STANDARD_SEMAPHORE[letter]
        # Offset both angles by 15° (well within 30° tolerance)
        result = decode_semaphore(right_angle + 15, left_angle - 15)
        assert result == letter, (
            f"With ±15° offset: decode_semaphore({right_angle+15}, {left_angle-15}) "
            f"= '{result}', expected '{letter}'"
        )

    def test_unknown_angles_return_question_mark(self):
        """Angles that don't match any letter should return '?'."""
        result = decode_semaphore(999, 999)
        assert result == "?"
```

- [ ] **Step 2: Run all decode tests**

```bash
python -m pytest tests/test_semaphore_translator.py::TestDecodeSemaphore -v
```

Expected: All tests PASS (27 exact, 1 uniqueness, 26 tolerance, 1 unknown).

- [ ] **Step 3: Commit**

```bash
git add tests/test_semaphore_translator.py
git commit -m "test: add decode_semaphore tests for all 26 letters + tolerance"
```

---

### Task 6: Write integration tests (Hailo required)

**Files:**
- Modify: `tests/test_semaphore_translator.py`

- [ ] **Step 1: Add integration test class with image download fixture**

Append to `tests/test_semaphore_translator.py` (imports already at top of file from Task 3):

```python
SEMAPHORE_DATA_DIR = Path(__file__).parent / "data" / "semaphore"

# Map of letter -> URL for reference semaphore images
# These should be public domain / educational images of people performing semaphore
# TODO: populate with actual URLs during implementation once suitable images are found
SEMAPHORE_IMAGE_URLS = {
    # "A": "https://example.com/semaphore_a.jpg",
}


@pytest.fixture(scope="session")
def semaphore_images():
    """Download semaphore reference images if not already present."""
    if not SEMAPHORE_IMAGE_URLS:
        pytest.skip("No semaphore reference image URLs configured yet")

    SEMAPHORE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = {}

    for letter, url in SEMAPHORE_IMAGE_URLS.items():
        ext = url.rsplit(".", 1)[-1].split("?")[0]
        image_path = SEMAPHORE_DATA_DIR / f"{letter}.{ext}"
        if not image_path.exists():
            try:
                urllib.request.urlretrieve(url, image_path)
            except Exception as e:
                pytest.skip(f"Failed to download semaphore image for '{letter}': {e}")
        downloaded[letter] = str(image_path)

    if not downloaded:
        pytest.skip("No semaphore images available")
    return downloaded


@pytest.mark.hailo
class TestSemaphoreIntegration:
    """Integration tests that run the full pipeline on reference images.

    Requires Hailo hardware. Skip with: pytest -m 'not hailo'
    """

    def test_pipeline_decodes_letter(self, semaphore_images):
        """Run the semaphore translator on each reference image and verify the decoded letter."""
        app_path = (
            "community/apps/pipeline_apps/semaphore_translator/semaphore_translator.py"
        )

        for expected_letter, image_path in semaphore_images.items():
            result = subprocess.run(
                [
                    "python", app_path,
                    "--input", image_path,
                    "--no-display",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(Path(__file__).parent.parent),
            )

            # Parse stdout for "Letter: X" lines
            detected_letter = None
            for line in result.stdout.splitlines():
                if "Letter:" in line:
                    # Format: "... Letter: X"
                    detected_letter = line.split("Letter:")[-1].strip()

            assert detected_letter == expected_letter, (
                f"Image {image_path}: expected '{expected_letter}', "
                f"got '{detected_letter}'\nstdout: {result.stdout[-500:]}"
            )
```

- [ ] **Step 2: Run integration tests (they will skip if no URLs configured)**

```bash
python -m pytest tests/test_semaphore_translator.py::TestSemaphoreIntegration -v
```

Expected: SKIPPED with "No semaphore reference image URLs configured yet"

- [ ] **Step 3: Commit**

```bash
git add tests/test_semaphore_translator.py
git commit -m "test: add integration test scaffold for semaphore pipeline with image input"
```

---

### Task 7: Run full test suite and verify

**Files:**
- None (verification only)

- [ ] **Step 1: Run all unit tests**

```bash
cd /home/giladn/tappas_apps/repos/hailo-community-projects
python -m pytest tests/test_semaphore_translator.py -v -m 'not hailo'
```

Expected: All unit tests PASS (8 angle + 14 discretize + 27 exact decode + 1 uniqueness + 26 tolerance + 1 unknown = 77 tests).

- [ ] **Step 2: Verify import still works end-to-end**

```bash
python -c "
from community.apps.pipeline_apps.semaphore_translator.semaphore_translator import (
    SEMAPHORE_ALPHABET, compute_arm_angle, discretize_angle, decode_semaphore
)
# Quick sanity: R = both arms horizontal to opposite sides
assert decode_semaphore(90, 270) == 'R'
# N = both arms low to opposite sides
assert decode_semaphore(45, 315) == 'N'
# REST = both arms down
assert decode_semaphore(0, 0) == 'REST'
print('All sanity checks passed')
"
```

- [ ] **Step 3: Check for any unstaged changes**

```bash
git status
```

If any relevant files are still unstaged, add them explicitly (do NOT use `git add -A` — the repo has untracked files like `access_log.csv` and `venv_hailo_apps/` that should not be committed):

```bash
git add community/apps/pipeline_apps/semaphore_translator/semaphore_translator.py tests/test_semaphore_translator.py
git commit -m "chore: finalize semaphore translator update"
```
