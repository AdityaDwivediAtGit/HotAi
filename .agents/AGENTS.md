# HotAI Project Agents Rules

## Roles
- **VisionCoder**: Responsible for handling all video processing tasks, specifically OpenCV-based motion extraction.
- **AnalyticsCoder**: Responsible for data clustering, anomaly detection logic, and DBSCAN implementation.

## Guidelines
- Always prioritize performance. Video processing should run fast; downscale frames before processing if using dense optical flow.
- Maintain a clean separation of concerns between computer vision tasks and analytical clustering tasks.
