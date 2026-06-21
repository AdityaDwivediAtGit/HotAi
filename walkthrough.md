# HotAI MVP Walkthrough

## Summary of Accomplishments

I have successfully initialized the multi-agent architecture and built the anomaly and hotspot detection pipeline as part of the HotAI MVP. 

### Multi-Agent Configuration
1. Created `.agents/AGENTS.md` containing behavioral guidelines for the agents.
2. Created `agent.yaml` configuration with the roles for the sub-agents.
3. Defined **VisionCoder** and **AnalyticsCoder** natively in the workspace context for future invocations.

### Pipeline Implementation
The pipeline comprises the following connected scripts:
- **`src/ingestion.py`**: A mock script capturing frames from a CCTV `mp4` feed.
- **`src/optical_flow.py`**: OpenCV implementation utilizing Lucas-Kanade optical flow on Shi-Tomasi corners to rapidly determine motion magnitudes and angles in real-time.
- **`src/clustering.py`**: A fast Density-Based Spatial Clustering of Applications with Noise (DBSCAN) logic determining hotspots of motion based on proximity and density.
- **`src/pipeline.py`**: The overarching logic reading a downloaded sample video (`people-detection.mp4`), plotting heatmap overlays on hotspots, calculating mocked GPS positions (based near Times Square), and saving everything to disk.

## Output Artifacts

We ran the pipeline against a sample people-walking CCTV video, stopping after the first 10 seconds of processing to ensure rapid delivery. The pipeline correctly tracked individuals and clustered them when they moved in close proximity, defining a visual "hotspot".

### Visual Output
You can review the output heatmap overlaid on the mock CCTV footage below. Rapid/dense motions are highlighted with an active red heatmap circle, complete with a density score tracking metric.

![Hotspot Output Video](file:///C:/Users/dwive/.gemini/antigravity/brain/045ebdb8-4ea8-42ff-b4ad-1586e409db56/hotspot_output.mp4)

### Hotspot Log Output
Here is the raw output from the analytics cluster detailing the density and timestamp, matched back to our mock GPS coordinates:

[Hotspots JSON Log](file:///C:/Users/dwive/.gemini/antigravity/brain/045ebdb8-4ea8-42ff-b4ad-1586e409db56/hotspots_log.json)

> [!TIP]
> The MVP pipeline operates significantly fast since we track feature points instead of processing dense optical flow pixel-by-pixel. Future iterations could integrate background subtraction or deep-learning-based object tracking.
