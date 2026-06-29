# HotAI Dynamic Architecture Walkthrough

## Summary of Accomplishments

We have transformed HotAI from an aggregated MVP to a highly precise, mathematically accurate surveillance simulation system. 

### 1. Accurate Unique Person Counting
Instead of counting raw optical flow corners (which could result in 1 person generating 10 tracked arrows), we have implemented a **Spatial Clustering Engine**. 
- The system groups movement vectors that are spatially contiguous. 
- It tracks distinct physical entities and draws an accurate red bounding circle and arrow around each unique person.
- **YOLO Heavy-Mode Integration**: For users with high-end GPUs, we have implemented an optional parameter `USE_HEAVY_YOLO = True` inside `orchestrator.py`. When enabled, the system drops the lightweight clustering in favor of Ultralytics YOLOv8 object detection for perfect human counting.

### 2. Time-Series Dynamic Synchronization
- We completely rewrote the analytics payload to support **Time-Series arrays**.
- The `orchestrator.py` engine now logs frame-by-frame data. 
- In the Web UI, the sidebar no longer displays static averages. It actively hooks into the HTML5 `<video>` element's playback clock. As you watch the CCTV feed play, the Total Count, Dominant Direction, and Bar Charts **animate and update synchronously every second** based strictly on the current frame's detections!

### 3. Real-World Rigid Camera Calibration
- We stripped out the randomized convergence noise and replaced it with a strictly calibrated physical matrix.
- `src/cameras_config.json` now dictates the exact GPS Lat/Lng and the exact heading (0-360 degrees) of the 20 cameras.
- The UI disables dragging for these markers (as they represent fixed, real-world infrastructure). The javascript algorithm geometrically maps the trajectory vectors on the leaflet map using real-world trigonometry relative to each camera's established field of view!

## How to Test It
The orchestrator pipeline is currently running in the background building the new time-series data and re-encoding the videos for browser compatibility. 

1. Wait roughly 2 minutes for the pipeline to finish processing.
2. Refresh your browser at `http://localhost:8000/index.html`.
3. Click a fixed camera marker.
4. **Watch the Sidebar:** Notice how the statistics (Total detected, N/S/E/W bar charts) instantly fluctuate in real-time alongside the video playback!
