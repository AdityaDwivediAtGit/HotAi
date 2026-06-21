# HotAI MVP Implementation Plan

This document outlines the proposed implementation plan to set up the multi-agent architecture and build the basic anomaly and hotspot detection pipeline for HotAI.

## User Review Required

Please review the proposed multi-agent architecture and the video processing pipeline. Let me know if you have a specific video file (`.mp4`) that you'd like to use for testing, or if I should generate/download a mock video.

> [!WARNING]
> Processing video using optical flow and DBSCAN clustering can be computationally intensive. Ensure that the test video length and resolution are reasonable for the MVP testing phase.

## Open Questions

> [!IMPORTANT]
> 1. Do you have a preferred test `.mp4` video file we should use, or should I procure a generic sample video representing CCTV footage?
> 2. What are the mock GPS coordinates (latitude/longitude) you'd like to assign to the test video?
> 3. Do you have any specific preferences between Lucas-Kanade (sparse) and Gunnar Farneback's (dense) optical flow methods? Dense optical flow provides more data but is more computationally heavy. I recommend Gunnar Farneback's algorithm for better crowd density analysis.

## Proposed Changes

### Multi-Agent Architecture
I will set up the workspace for agent customizations.
#### [NEW] .agents/AGENTS.md
#### [NEW] agent.yaml

### Ingestion & Processing Pipeline
These scripts will form the core MVP. I will coordinate with `VisionCoder` and `AnalyticsCoder` sub-agents to build these.
#### [NEW] src/ingestion.py (Mock CCTV ingestion & GPS mapping)
#### [NEW] src/optical_flow.py (Motion vector extraction via OpenCV)
#### [NEW] src/clustering.py (DBSCAN hotspot detection via scikit-learn)
#### [NEW] src/pipeline.py (Main orchestrator linking ingestion, flow, and clustering)
#### [NEW] requirements.txt (Dependencies: opencv-python, scikit-learn, numpy)

## Verification Plan

### Automated Tests
- N/A for MVP script structure. I will ensure all Python scripts execute successfully.

### Manual Verification
- We will run `pipeline.py` on a sample video.
- **Visual Output:** A generated video artifact with a heatmap overlay indicating high-density clusters.
- **Log Output:** A generated JSON file containing timestamped mock GPS coordinates and density scores of detected hotspots.
