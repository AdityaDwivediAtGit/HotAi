# HotAI Enhancement Implementation Plan

This document outlines the architectural changes required to support 20 unique video feeds, live CCTV fetching, advanced per-camera analytics, and rendering actual video footage inside the Web UI.

## Goal Description
The objective is to upgrade the HotAI MVP from a simulated vector pool to a robust system that processes 20 distinct video feeds (with optional live public CCTV fetching), computes advanced directional analytics (crowd flow, counts, densities), and visually renders the processed video feeds (complete with individual and overall crowd movement arrows) inside the interactive map UI.

## Proposed Changes

### 1. Data Ingestion: Live Public CCTV & 20 Unique Feeds
- **[MODIFY] `src/generate_db.py` -> `src/orchestrator.py`**: We will replace the simple DB generator with a robust orchestrator.
- **Live Fetching Engine**: Implement an optional flag to fetch live `.m3u8` streams (e.g., public traffic/street cameras). If unavailable, the script will programmatically download 20 distinct short pedestrian clips (e.g., from public GitHub datasets or CC0 video APIs) to ensure 20 unique feeds.
- **Video Processing**: The script will process 10-15 seconds of each video (to keep execution time reasonable) and save the *processed* `.mp4` video (with drawn arrows) to a `ui/videos/` directory.

### 2. Advanced Camera Analytics
- **[MODIFY] `src/optical_flow.py`**:
  - Calculate individual tracking arrows (blue/red).
  - Calculate the **Overall Crowd Movement Vector** (average of all significant motion) and render it as a large **Green Arrow** on the video frame.
  - Compute directional distribution (e.g., 45% moving North, 30% East, etc.).
  - Estimate camera orientation based on dominant flow.
  - Compute a probability/confidence score for the dominant direction.
- **JSON Payload Expansion**: The output JSON will now contain a `cameras` array, where each camera object holds its assigned GPS coordinate, the filepath to its processed `.mp4` video, and the rich analytics object (counts, density, direction distribution).

### 3. UI Visualization Upgrades
- **[MODIFY] `ui/index.html` & `ui/map.js`**:
  - The Leaflet map will remain the central component.
  - When you click on a camera marker on the map, a UI modal or side-panel will open.
  - This panel will **play the actual processed video footage** for that specific camera, displaying the individual and overall crowd arrows.
  - The panel will also display the rich analytics (Directional breakdown, Crowd Density, Total Count) in a clean, modern glassmorphism UI.

## Open Questions

> [!WARNING]
> Processing 20 unique video files sequentially using OpenCV optical flow can take significant time (potentially 10-20 minutes depending on resolution and length). 

> [!IMPORTANT]
> 1. **Video Length**: To keep the build time reasonable for this execution, I propose processing only **5 seconds** of footage for each of the 20 cameras. Is this acceptable?
> 2. **Public CCTV Source**: Relying on live `.m3u8` streams can be highly brittle (streams frequently go offline). I will implement a fallback to download 20 static CC0 pedestrian clips. Do you have a preferred list of public CCTV URLs, or should I curate a fallback list of 20 generic traffic/pedestrian URLs?
> 3. **UI Video Rendering**: Is it acceptable to display the video feed in a popup/sidebar when a camera marker is *clicked* on the map, rather than trying to play 20 videos simultaneously on the screen (which would crash most browsers)?

## Verification Plan
### Manual Verification
- Run `python src/orchestrator.py`.
- Verify it downloads/fetches 20 unique videos and processes them into `ui/videos/`.
- Open `ui/index.html`.
- Click on various camera markers. Ensure the sidebar opens, plays the correct unique video (with green overall arrows), and displays the detailed analytics.
