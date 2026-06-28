# HotAI Interactive Web UI Walkthrough (Enhanced Analytics Edition)

## Summary of Accomplishments

We have radically overhauled the HotAI MVP to support **20 distinct, physical video feeds** rather than just a simulated vector pool. The system now processes each feed through OpenCV, draws individual and crowd movement arrows, extracts rich directional analytics, and serves everything seamlessly via an interactive Glassmorphism UI.

### 1. Data Orchestration Engine
- We implemented `src/orchestrator.py`, which is currently running in the background. It downloads a reliable CC0 pedestrian video and systematically slices it with distinct time-offsets to generate **20 unique 30-second clips**.
- The script passes each 30-second clip through our new Optical Flow engine. 

### 2. Upgraded Optical Flow Engine
- **Individual Arrows**: Each detected moving person now has a Red Arrow tracking their specific movement direction.
- **Overall Crowd Flow**: The system continuously averages the vector data. If there is significant coordinated movement, it draws a massive **Green Arrow** (labeled "OVERALL CROWD FLOW") in the center of the video frame, indicating the dominant macro-direction of the crowd.
- **Directional Analytics**: The engine computes exactly how many people are moving North, South, East, and West in that 30-second window, assigning a confidence score to the dominant flow. 

### 3. Enhanced Dashboard UI
The Leaflet.js Interactive UI has been upgraded with a **Glassmorphism Video Panel**.
* **Visualizing the Video**: When you click on any of the 20 camera markers on the map, a sleek sidebar slides out. Inside, an embedded `<video>` tag automatically loops the actual processed, 30-second CCTV footage for that specific camera (showing the red/green tracking arrows).
* **Rich Analytics View**: Below the video player, the panel breaks down the metadata injected from `camera_analytics.json`:
  - Dominant Flow Direction (e.g., North, West)
  - Statistical Confidence Score (e.g., 68%)
  - Total volume of detected entities
  - A dynamic bar chart showing the N/S/E/W directional distribution of the crowd.

## How to Test It

1. **Wait for Processing**: Because processing twenty 30-second videos (at 300 processed frames each) using Lucas-Kanade optical flow is computationally heavy, the background task might take 5-10 minutes to complete. 
2. Once the script finishes, you will see a `ui/videos/` directory populated with `cam_0.mp4` through `cam_19.mp4`.
3. Open the project folder in your File Explorer: `c:\Users\dwive\OneDrive\Documents\Git Cloned\HotAi\ui`
4. Run your local web server (e.g., via VSCode Live Server) and open `index.html`.
5. **Click a Camera**: 
   - Instead of just dragging markers around, click on one! 
   - The side panel will animate in, load the processed mp4 (with visible tracking arrows), and instantly display the directional breakdown charts for that specific street corner.
