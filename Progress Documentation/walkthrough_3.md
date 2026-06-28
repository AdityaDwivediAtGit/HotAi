# HotAI Interactive Web UI Walkthrough

## Summary of Accomplishments

To extensively test the predictive hotspot detection across a massive scale (20 different cameras), we built a fully transparent, interactive Web UI that lets you manually map CCTV coordinates and watch the convergence predictions happen in real-time.

### Multi-Camera Simulation & Data Extraction
Instead of hardcoding a single setup, we built an engine to make testing flexible:
1. **Vector Extraction**: We used `src/generate_db.py` to process our sample pedestrian tracking footage and extract a database of raw "human movement vectors". 
2. **20-Camera Network**: Inside the UI, we simulate 20 distinct cameras. The UI pulls the raw vectors and artificially calibrates their angles based on where you place the camera markers on the map, mathematically simulating 20 different crowds converging on a central location (Times Square).

### The Web Application (`ui/index.html`)
The application was built prioritizing speed, transparency, and premium aesthetics:
- **Core Technology**: Static HTML and Vanilla JavaScript for maximum portability. No heavy backend server is required.
- **Leaflet.js Mapping**: We use CARTO's dark-mode maps for a sleek, modern, surveillance-style aesthetic.
- **Client-Side DBSCAN**: The `map.js` file contains a custom JavaScript implementation of DBSCAN. Every time you move a camera, it instantly re-projects the 30-45 minute trajectories of all moving entities, calculates the new cluster densities, and draws the hotspots.

## How to Test It

To try the interactive simulation yourself:
1. Open the project folder in your File Explorer: `c:\Users\dwive\OneDrive\Documents\Git Cloned\HotAi\ui`
2. Since it relies on fetching a local JSON file (`raw_vectors.json`), it's best to run a quick local server, or use an IDE like VSCode with a "Live Server" extension. (Alternatively, you can open `index.html` directly in Firefox, as it allows local file fetching, though Chrome restricts it).
3. **Play with the map**: 
   - You will see 20 blue markers representing the CCTV cameras.
   - **Click and drag** any camera marker to a new coordinate.
   - Watch the blue trajectory lines and the **Glowing Hotspot Map** (Yellow -> Orange -> Red) instantly recalculate based on the new origin of the crowd!

> [!TIP]
> Dragging multiple cameras into a tight perimeter will cause their predicted paths to overlap heavily, immediately spiking the density probability and turning the convergence zone bright red. This proves the system correctly aggregates and flags areas where people are flocking to from multiple distinct origin points!
