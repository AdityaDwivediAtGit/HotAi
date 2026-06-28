# How HotAI Works (In Simple Terms)

Welcome to the HotAI project! If you're wondering what all the technical words mean and how this application actually does its job, you're in the right place. 

## 📖 Simple Dictionary (Terminologies)

Here are the key terms used in the HotAI project, explained simply:

- **CCTV (Closed-Circuit Television):** Standard security or traffic cameras. Our app processes videos recorded by these cameras.
- **Optical Flow:** A computer vision technique that compares two consecutive frames (pictures) of a video to figure out which direction things are moving. Imagine holding up two photos taken a second apart and drawing arrows to show where a person stepped.
- **Lucas-Kanade Method:** A specific, very fast type of "Optical Flow." Instead of looking at every single pixel (which is slow), it only looks at obvious features (like the corners of a person's shape) to track movement.
- **Motion Vectors:** The "arrows" created by the Optical Flow. A motion vector tells us two things: **Direction** (where the object is going) and **Magnitude** (how fast it is moving).
- **DBSCAN (Density-Based Spatial Clustering of Applications with Noise):** A very smart grouping tool. It looks at all our motion vectors and says, "If a lot of these arrows are packed closely together, they form a group (a cluster). If an arrow is all by itself, ignore it (it's just noise)."
- **Hotspot:** An area on the screen where DBSCAN found a dense group of moving objects. For example, a large crowd walking closely together.
- **Heatmap:** A visual layer placed over the video. In our app, we draw red circles over the hotspots. The redder or larger the circle, the higher the density of the crowd.

---

## ⚙️ How the Application Actually Works

The HotAI application works in a step-by-step pipeline. Imagine a factory assembly line where a video enters on one side, and a smart, analyzed video comes out the other.

### Step 1: Taking in the Video (Ingestion)
The application starts by opening a video file (like `.mp4`) to simulate a live CCTV camera feed. It also assigns a fake "GPS Coordinate" to this video so that if we detect an anomaly, we know where it happened in the real world.

### Step 2: Spotting Movement (Optical Flow)
The video is passed frame-by-frame (picture-by-picture) to the **VisionCoder** part of the app. 
1. The app looks at the frame and picks out distinctive points (like the edges of people).
2. It compares those points to the previous frame. 
3. It draws invisible "Motion Vectors" (arrows) showing exactly how those points moved.

### Step 3: Finding the Crowds (Clustering)
Now, we have a list of arrows floating around the screen. The **AnalyticsCoder** part of the app takes over.
1. It looks at the location of every single arrow.
2. It uses **DBSCAN** to group them. If 5 or 10 arrows are moving very close to each other, it marks them as a "Hotspot".
3. It ignores random, isolated movements (like a single bird flying by) so it doesn't trigger a false alarm.

### Step 4: Showing the Results (Visualization)
Finally, the app takes the original video and draws on it. 
1. It draws green arrows to show the raw movement it detected.
2. It draws glowing red circles (a heatmap) directly over the Hotspots it grouped together.
3. It writes a log in a text file (`.json`) saying: *"At this time, at this GPS location, we saw a crowd of this size."*

And that's it! The application constantly repeats this process, turning a normal video into a smart, anomaly-detecting surveillance tool.
