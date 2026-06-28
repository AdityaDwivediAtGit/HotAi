# Testing Documentation for HotAi

## Overview

This document provides a comprehensive guide for running and understanding the test suite for the HotAi application. The test suite validates core functionality including video ingestion, motion extraction, hotspot clustering, and end-to-end pipeline execution.

## Test Requirements

Before running tests, ensure the following dependencies are installed:

```bash
pip install -r requirements.txt
```

Required packages:
- `opencv-python` (4.13.0.92+)
- `scikit-learn` (1.7.2+)
- `numpy` (2.3.5+)

## Running Tests

### Run All Tests

```bash
python -m unittest tests.test_hotai
```

Expected output:
```
....
----------------------------------------------------------------------
Ran 4 tests in ~5.5s

OK
```

### Run Specific Test

```bash
python -m unittest tests.test_hotai.TestHotAi.test_mock_cctv_reads_frames
```

### Verbose Mode

```bash
python -m unittest tests.test_hotai -v
```

## Test Suite Overview

### Location
`tests/test_hotai.py`

### Test Class
`TestHotAi` - Contains 4 unit and integration tests

---

## Test Cases

### 1. `test_mock_cctv_reads_frames`

**Purpose:** Validates the `MockCCTV` video ingestion module.

**What it tests:**
- Synthetic video creation and file writing
- Video frame reading capability
- Frame format (BGR, 3 channels)

**Behavior:**
- Creates a temporary synthetic video file
- Reads the first frame using `MockCCTV`
- Asserts frame is valid and has correct shape

**Passes when:**
- Frame read is successful (`ret=True`)
- Frame is not None
- Frame has 3 color channels (BGR)

---

### 2. `test_motion_extractor_returns_vectors_for_moving_content`

**Purpose:** Validates the `MotionExtractor` optical flow extraction module.

**What it tests:**
- Motion vector extraction from video sequences
- Correct handling of initial frames (no motion expected)
- Output format of motion vectors

**Behavior:**
- Creates a synthetic video with a moving rectangle
- Processes two consecutive frames
- First frame returns empty motion vectors (no previous frame to compare)
- Second frame extracts motion vectors

**Passes when:**
- First frame returns 0 motion vectors
- Second frame returns motion vectors (or empty if motion is minimal)
- Motion vectors contain required keys: `x`, `y`, `dx`, `dy`, `magnitude`, `angle`
- Returned frames are numpy arrays

---

### 3. `test_hotspot_detector_groups_motion_vectors`

**Purpose:** Validates the `HotspotDetector` clustering module.

**What it tests:**
- DBSCAN clustering of motion vectors
- Proper grouping of spatially-close motion points
- Hotspot metadata (center, density score)

**Behavior:**
- Creates 10 synthetic motion vectors in two distinct spatial clusters:
  - Cluster 1: 5 vectors around (10, 10)
  - Cluster 2: 5 vectors around (100, 100)
- Clusters with eps=20 and min_samples=3
- Detects hotspots from the clustered vectors

**Passes when:**
- Exactly 2 hotspots are detected (noise excluded)
- Each hotspot has `center_x` and `center_y` fields
- Each hotspot has `density_score >= 3` (minimum cluster size)

---

### 4. `test_run_pipeline_produces_video_and_json`

**Purpose:** End-to-end validation of the complete pipeline.

**What it tests:**
- Full pipeline execution from video to outputs
- Output video file generation and validity
- Output JSON log file generation and structure

**Behavior:**
- Creates a temporary synthetic video (30 frames)
- Runs `run_pipeline()` with this video
- Verifies output video is readable by OpenCV
- Parses and validates output JSON log structure

**Passes when:**
- Output video file exists and is readable
- Output JSON file exists and is valid JSON
- JSON contains a list of log entries
- Each log entry has `timestamp` and `mock_gps` fields
- Mock GPS coordinates match input

---

## Helper Function

### `create_synthetic_video(path, frame_count=60, width=320, height=240)`

Creates a temporary MP4 video file with a moving white rectangle for testing.

**Parameters:**
- `path` (Path): Output file path
- `frame_count` (int, default=60): Number of frames to generate
- `width` (int, default=320): Video width in pixels
- `height` (int, default=240): Video height in pixels

**Returns:**
- `path` (str): Path to the created video file

**Usage:**
```python
video_path = Path(tmpdir) / "test_video.mp4"
create_synthetic_video(video_path, frame_count=30, width=640, height=480)
```

---

## Test Structure

### Temporary Directories

All tests use Python's `tempfile.TemporaryDirectory()` to isolate test artifacts and avoid polluting the filesystem. Temporary files are automatically cleaned up after each test.

### Imports

```python
import unittest           # Test framework
import tempfile          # Temporary file/dir creation
from pathlib import Path # Path utilities
import cv2               # OpenCV for video operations
import numpy as np       # NumPy for arrays
```

---

## Continuous Testing

### Run Tests After Code Changes

```bash
# After modifying src/ingestion.py, src/optical_flow.py, src/clustering.py, or src/pipeline.py
python -m unittest tests.test_hotai
```

## Artifacts

When the pipeline runs during tests or manually, outputs are written into the repository `artifacts/` directory (project root). Check these files for visual verification and logs:

- `artifacts/hotspot_output.mp4`
- `artifacts/hotspots_log.json`

### Automated Testing (Recommended)

Use file watchers or CI/CD pipelines to run tests automatically:

```bash
# Example with pytest-watch (if installed)
ptw tests/test_hotai.py
```

---

## Extending the Test Suite

To add new tests:

1. Open `tests/test_hotai.py`
2. Add a new method to `TestHotAi` class starting with `test_`
3. Use assertions to validate behavior:

```python
def test_new_feature(self):
    """Test description."""
    result = some_function()
    self.assertEqual(result, expected_value)
    self.assertTrue(condition)
    self.assertGreater(value, threshold)
```

Common assertions:
- `self.assertEqual(a, b)` - Check equality
- `self.assertTrue(condition)` - Check boolean true
- `self.assertFalse(condition)` - Check boolean false
- `self.assertGreater(a, b)` - Check a > b
- `self.assertGreaterEqual(a, b)` - Check a >= b
- `self.assertIn(item, list)` - Check item in list
- `self.assertRaises(Exception, func)` - Check exception raised

---

## Troubleshooting

### Tests Fail with Import Errors

**Problem:** `ModuleNotFoundError: No module named 'ingestion'`

**Solution:** Ensure you're running tests from the project root directory:
```bash
cd c:\Users\dwive\OneDrive\Documents\Git Cloned\HotAi
python -m unittest tests.test_hotai
```

### Tests Fail with Missing Dependencies

**Problem:** `ModuleNotFoundError: No module named 'cv2'`

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Slow Test Execution

Tests should complete in ~5.5 seconds. If slower:
- Check system resources (CPU, disk)
- Ensure no other heavy processes are running
- Verify video codec is available (mp4v)

### Video Codec Issues

**Problem:** `VIDEOIO ERROR`

**Solution:** Ensure FFmpeg or equivalent codec libraries are installed. On Windows, this usually comes with OpenCV automatically.

---

## Test Coverage

Current coverage:
- **Ingestion Module**: 1 test (MockCCTV)
- **Optical Flow Module**: 1 test (MotionExtractor)
- **Clustering Module**: 1 test (HotspotDetector)
- **Pipeline Module**: 1 test (End-to-end)

**Total: 4 tests**

---

## Additional Notes

- All tests are **unit tests** combined with **integration tests**
- Tests are **isolated** (each creates its own temporary resources)
- Tests are **deterministic** (same input → same output)
- Tests execute in **~5.5 seconds**
- No external files or API calls required

---

## Contact & Support

For issues or questions about the test suite, refer to the main `README.md` or create an issue in the project repository.
