# Semaphore Translator Update — Design Spec

## Goal

Update the semaphore_translator app to align with the international maritime semaphore flag standard, add an image source type to the GStreamer SOURCE_PIPELINE helper, and add tests validated against reference images downloaded from the web.

## Scope

Minimal: fix the mapping, add image source support, add tests. No new utility modules or architectural changes.

## 1. Fix SEMAPHORE_ALPHABET Mapping

**File:** `community/apps/pipeline_apps/semaphore_translator/semaphore_translator.py`

**Problem:** The current `SEMAPHORE_ALPHABET` dict has numerous incorrect mappings. Only C, R, and S are correct. Entries for H, W, and X are flagged as "not standard." The angle convention comments mix perspectives.

**Key insight:** The `compute_arm_angle()` function computes angles that correspond to the **signaler's perspective** (not image/viewer coordinates). This is because the `atan2(-dx, dy)` formula with COCO keypoints (which use the person's own left/right naming) produces angles where:
- 0° = straight down
- 90° = signaler's right (image LEFT, since person faces camera)
- 180° = straight up
- 270° = signaler's left (image RIGHT)

**No conversion is needed.** The standard semaphore positions (defined from signaler's perspective) can be used directly as lookup values. The previous spec incorrectly proposed an `image_angle = (360 - signaler_angle) % 360` conversion.

**Corrected SEMAPHORE_ALPHABET dict:**

Based on the international maritime semaphore standard (references: [ANBG Semaphore](https://www.anbg.gov.au/flags/semaphore.html), [Wikipedia Flag Semaphore](https://en.wikipedia.org/wiki/Flag_semaphore)):

```python
# Format: (right_arm_angle, left_arm_angle): "LETTER"
# Angles from signaler's perspective, clockwise from down:
#   0° = down, 45° = down-right, 90° = right, 135° = up-right,
#   180° = up, 225° = up-left, 270° = left, 315° = down-left
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

**Position pair verification:** All 26 letters use unique unordered pairs from the 8 positions. The 2 unused pairs are {135°,315°} and {180°,225°}. No duplicate position pairs exist.

**Existing code comparison — what changes:**
- **Correct (unchanged):** C=(135,0), R=(90,270), S=(90,315)
- **All other 23 letters:** incorrect in the current code, replaced with standard values
- **Duplicate entries removed:** H had 2 entries, W had 2, X had 2

## 2. Add Image Source to SOURCE_PIPELINE

**File:** `hailo-apps-infra/hailo_apps/python/core/gstreamer/gstreamer_helper_pipelines.py`

**Note:** This modifies the hailo-apps-infra submodule (intentional, per user approval). Changes will need to be upstreamed separately.

### get_source_type()

Add detection for image file extensions before the `"file"` fallthrough:
```python
elif input_source.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
    return "image"
```

Case-insensitive matching handles `IMAGE.JPG`, `photo.PNG`, etc.

### SOURCE_PIPELINE()

Add optional `num_buffers` parameter (default: 30). Add `"image"` source type branch:

```python
elif source_type == "image":
    source_element = (
        f'multifilesrc location="{video_source}" loop=true num-buffers={num_buffers} ! '
        f'decodebin name={name}_decodebin ! '
    )
```

**Details:**
- Uses `multifilesrc` (already proven in this repo: face_recognition, cat_food_monitor apps)
- `loop=true` re-reads the same file to produce multiple frames
- `num-buffers` controls how many frames are pushed (default 30)
- No explicit caps — matches the proven pattern used by cat_food_monitor and face_recognition, which use `multifilesrc ! decodebin` without caps. `decodebin` auto-detects the image format (JPEG, PNG, BMP, GIF) and handles decoder selection automatically
- No `videoflip` for image sources (no mirror needed)
- The shared downstream pipeline (videoscale, videoconvert, videorate, fps caps) works unchanged

**Multi-image support:** For `--input img1.jpg,img2.jpg,...`, the app's argument parser splits on commas and iterates, running the pipeline once per image. This is handled at the app level, not in SOURCE_PIPELINE.

**Usage:**
```bash
python semaphore_translator.py --input image.jpg
python semaphore_translator.py --input image1.jpg,image2.jpg,image3.jpg
```

## 3. Tests

**File:** `tests/test_semaphore_translator.py`

### Unit Tests (no hardware)

Test the pure logic functions with known inputs:

- **`test_compute_arm_angle`**: Pass known (shoulder_x, shoulder_y, wrist_x, wrist_y) coordinates, assert expected angles. Cover all 8 cardinal directions (0°, 45°, 90°, ..., 315°).
- **`test_discretize_angle`**: Pass angles at boundaries and mid-points, assert correct 45° snapping (e.g., 22° → 0°, 23° → 45°, 44° → 45°).
- **`test_decode_semaphore_all_letters`**: For each of the 26 standard letters, pass the exact (right_angle, left_angle) pair and assert the correct letter is returned. This validates the entire mapping table against the standard.
- **`test_decode_semaphore_tolerance`**: Pass slightly off-center angles (within `ANGLE_TOLERANCE=30°`) and verify they still decode correctly.

### Integration Tests (Hailo required)

- Marked with `@pytest.mark.hailo` so they can be skipped without hardware.
- **Test fixture** downloads standard semaphore reference images from the web into `tests/data/semaphore/`. If download fails, tests are skipped gracefully (`pytest.skip`).
- **Test mechanism:** Run the semaphore translator as a subprocess with `--input <image>`, capture stdout, parse for the `"Letter: X"` line from the callback output (printed every 30 frames at line 310-311 of `semaphore_translator.py`).
- With `num_buffers=30` and `stable_threshold=10`, a single image fed 30 times will produce a stable letter after 10 identical frames — sufficient for detection.
- Assert decoded letter matches the expected letter from the image filename/label.

### Dataset Source

- Primary: Download semaphore flag reference images from educational/public domain sources (e.g., Wikimedia Commons semaphore illustrations, ANBG semaphore diagrams)
- Fallback: If images cannot be downloaded, integration tests skip gracefully rather than failing
- Storage: `tests/data/semaphore/` (not checked into git, downloaded on-the-fly)

## Files Modified

| File | Change |
|---|---|
| `hailo-apps-infra/.../gstreamer_helper_pipelines.py` | Add `"image"` source type to `get_source_type()` and `SOURCE_PIPELINE()`, add `num_buffers` param |
| `community/.../semaphore_translator.py` | Replace `SEMAPHORE_ALPHABET` dict with corrected standard mapping, fix angle convention comments |
| `tests/test_semaphore_translator.py` | New file: unit tests (no hardware) + integration tests (`@pytest.mark.hailo`) |

## Out of Scope

- No new utility modules or runner classes.
- No additional semaphore signals (numerals, attention, error, cancel).
- No refactoring of existing code structure.
- No README updates beyond what's needed for accuracy.
