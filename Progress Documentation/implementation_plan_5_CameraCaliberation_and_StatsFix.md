# HotAI Dynamic Synchronization & Calibration Plan

This plan addresses the critical gaps in the MVP by upgrading the static analytics into a real-time, synchronized dashboard with mathematically calibrated cameras and proper object-level counting.

## Goal Description
Transform the system from an aggregated, static prototype into a highly accurate simulation where:
1. Video playback and UI statistics are perfectly synchronized frame-by-frame.
2. People counting is based on unique physical entities, not raw optical flow corners.
3. Camera arrays are rigidly calibrated (position, heading, FOV) for true spatial trajectory projection.

## Proposed Changes

### 1. Accurate Object Counting (Clustering)
- **[MODIFY] `src/optical_flow.py`**:
  - Raw Lucas-Kanade optical flow tracks arbitrary corners. We will implement spatial grouping.
  - If multiple tracking points are moving in a similar direction and are within a specific pixel radius (e.g., 40 pixels) of each other, they will be clustered and counted as a **single unique person**.
  - This solves the issue where one person generates 5-10 random movement vectors.

### 2. Time-Series Data Orchestration
- **[MODIFY] `src/orchestrator.py`**:
  - Instead of accumulating a single static statistic for the entire 30-second video, the script will generate a **Time-Series JSON array**.
  - It will log the exact directional distributions and counts for every second of the video (e.g., `time: 0.5s -> 2 Left, 1 Right`).

### 3. Rigid Camera Calibration
- **[MODIFY] `src/orchestrator.py` & `ui/map.js`**:
  - We will replace the randomized mapping with a strictly calibrated camera array.
  - Each camera will be assigned:
    - Exact GPS Coordinates (`lat`, `lng`)
    - **Heading Angle** (e.g., 90° East)
    - **Focal Scale** (Pixels to Meters conversion)
  - The UI will use these exact geometric parameters to rotate and scale the live vectors onto the Leaflet map, ensuring the convergence is mathematically accurate.

### 4. Dynamic, Synchronized UI
- **[MODIFY] `ui/map.js` & `ui/index.html`**:
  - Add a `timeupdate` event listener to the HTML5 `<video>` element.
  - As the video plays, the Javascript will continuously poll the `currentTime` and fetch the exact corresponding frame metrics from the Time-Series JSON.
  - The sidebar metrics (Dominant Direction, Counts, Confidence, Bar Charts) will dynamically animate and update in real-time, perfectly synced with the video playback.

## User Review Required

> [!WARNING]
> Because we must generate time-series arrays and apply clustering algorithms on top of the optical flow for 20 videos, the execution time for `orchestrator.py` will increase slightly.

## Open Questions

> [!IMPORTANT]
> 1. **Calibration Placement**: Should I programmatically generate the calibration matrices (e.g., arranging the 20 cameras in a perfect circle all mathematically facing the exact center with a 0-360 degree heading array), or do you want to define specific real-world coordinates and headings? (A programmatic circle is best for proving the algorithm works seamlessly).
> 2. **Person Clustering**: Using spatial clustering on Optical Flow points is fast and runs natively on CPU. Implementing a deep learning model (like YOLO) to count people perfectly would take hours to process 20 videos on a CPU. Is the fast clustering approach acceptable for this MVP?

## Verification Plan
1. Execute the new `orchestrator.py`.
2. Open the UI, click a camera, and watch the video play.
3. Verify that the numbers in the sidebar change dynamically every second, perfectly reflecting the physical people walking in the video clip at that exact timestamp.
4. Drag a camera and verify the projected trajectory mathematically respects its assigned Heading Angle.
