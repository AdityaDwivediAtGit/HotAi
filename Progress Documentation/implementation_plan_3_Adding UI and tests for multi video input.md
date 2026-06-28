# Multi-Camera Testing & Map Visualization Plan

This document outlines the approach for testing the predictive convergence logic across 5 different video feeds and building a user-friendly Web UI to visualize the results on a map.

## Goal Description
To extensively test the predictive hotspot detection, we will simulate a multi-camera environment. We will process 5 different video streams, assign each a unique GPS coordinate (e.g., surrounding a central square in Times Square), convert their pixel-based motion vectors into geographic (Latitude/Longitude) vectors, cluster them on a global coordinate plane, and visualize the cameras and the predicted hotspot on a Web Map UI.

## Proposed Changes

### 1. Data Preparation (Video Feeds)
- I will download 4 additional sample CCTV/pedestrian videos (or use different temporal cuts of a sample video to ensure varying motion data) to total 5 video sources.
- Assign 5 nearby GPS coordinates (forming a perimeter around a central point).

### 2. [MODIFY] `src/optical_flow.py` & `src/pipeline.py` (Geographic Mapping)
- Currently, projection happens in *pixel space*. To aggregate multiple cameras, we must translate pixels to geographic space.
- Introduce a `pixel_to_meters` scale factor.
- Convert the starting pixel `(x, y)` and the delta `(dx, dy)` into `(latitude, longitude)` and `(d_lat, d_lon)`.
- Pass these absolute geographic coordinates into the clustering algorithm.

### 3. [MODIFY] `src/clustering.py`
- Update the clustering logic to use Haversine distance or scale the `eps` parameter to handle Latitude/Longitude coordinate scales rather than pixel scales (e.g., setting `eps` to approx 0.0005 degrees, roughly 50 meters).

### 4. [NEW] `src/multi_pipeline.py`
- An orchestrator script that iterates over all 5 videos, extracts geographic motion vectors from all of them, combines the vectors into a single massive array, and runs the `HotspotDetector` once on the aggregated dataset.
- Saves the final output to `aggregated_hotspots.json`.

### 5. [NEW] `ui/index.html` & `ui/map.js`
- Create a simple, clean, and modern Web UI using HTML, Vanilla CSS, and Leaflet.js (a popular open-source mapping library).
- The map will plot:
  - 🎥 The 5 Camera Locations (with markers).
  - 🔴 The predicted Convergence Hotspots (drawn as glowing circles with gradient colors based on probability).
  - ↗️ (Optional) Lines indicating the trajectory from the cameras to the hotspot.

## Open Questions

> [!IMPORTANT]
> 1. **Video Sources**: I plan to use various open-source pedestrian tracking clips. If some clips don't have people moving towards the center, the convergence might not trigger. Is it acceptable if I artificially flip/rotate the video frames so that the simulated people are mathematically walking toward a central point to guarantee a hotspot test case?
> 2. **UI Framework**: I am proposing a static HTML webpage using Leaflet.js for the map. This is highly portable and doesn't require a backend server. Does this simple approach work for you?

## Verification Plan
### Automated Tests
- N/A for UI.

### Manual Verification
- Run `multi_pipeline.py` to generate the aggregated JSON.
- Open `ui/index.html` in a web browser.
- Verify that 5 camera markers are visible on the map.
- Verify that a predicted hotspot (e.g., Red/Orange circle) is rendered at the expected convergence zone.
