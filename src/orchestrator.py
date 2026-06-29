import cv2
import json
import os
import sys
import urllib.request
import math
from pathlib import Path

# Ensure the repository root is on sys.path so fix_videos.py can be imported from src/orchestrator.py
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fix_videos import convert
from optical_flow import MotionExtractor

def generate():
    os.makedirs(os.path.join("ui", "videos"), exist_ok=True)
    
    base_video = "sample.mp4"
    if not os.path.exists(base_video):
        print("Downloading sample video...")
        urllib.request.urlretrieve("https://github.com/intel-iot-devkit/sample-videos/raw/master/people-detection.mp4", base_video)
        
    num_cameras = 20
    analytics_db = []
    
    for i in range(num_cameras):
        print(f"Processing Camera {i+1}/{num_cameras}...")
        cap = cv2.VideoCapture(base_video)
        
        # Offset start time to make footage distinct
        start_frame = (i * 30) % max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        extractor = MotionExtractor()
        
        out_path = os.path.join("ui", "videos", f"cam_{i}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        
        total_counts = {"North": 0, "South": 0, "East": 0, "West": 0}
        total_people_detected = 0
        
        # 30 seconds of footage simulation (skip frames for speed, 10fps output)
        for _ in range(300):
            ret, _ = cap.read()
            ret, _ = cap.read()
            ret, frame = cap.read()
            if not ret or frame is None:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                
            processed_frame, vectors, overall_vec, dirs = extractor.extract_motion(frame)
            
            if out is None:
                h, w = processed_frame.shape[:2]
                out = cv2.VideoWriter(out_path, fourcc, 10.0, (w, h))
                
            out.write(processed_frame)
            
            for k, v in dirs.items():
                total_counts[k] += v
            total_people_detected += len(vectors)
            
        out.release()
        cap.release()
        
        dominant_dir = max(total_counts, key=total_counts.get)
        total = sum(total_counts.values())
        confidence = total_counts[dominant_dir] / total if total > 0 else 0
        
        angle = (i / num_cameras) * 3.14159 * 2
        r = 0.005 + (i * 0.0001)
        lat = 40.7580 + r * math.sin(angle)
        lng = -73.9855 + r * math.cos(angle)
        
        # Extract a generic trajectory for UI map simulation from dominant flow
        mock_dx = 0; mock_dy = 0
        if dominant_dir == "North": mock_dy = -5
        if dominant_dir == "South": mock_dy = 5
        if dominant_dir == "East": mock_dx = 5
        if dominant_dir == "West": mock_dx = -5

        analytics = {
            "id": f"Cam_{i}",
            "lat": lat,
            "lng": lng,
            "video_path": f"videos/cam_{i}.mp4",
            "mock_dx": mock_dx,
            "mock_dy": mock_dy,
            "metrics": {
                "total_movement_vectors": total_people_detected,
                "dominant_direction": dominant_dir,
                "confidence_score": round(confidence * 100, 2),
                "directional_distribution": total_counts,
                "camera_orientation_estimate": f"Facing {dominant_dir}"
            }
        }
        analytics_db.append(analytics)
        
    with open(os.path.join("ui", "camera_analytics.json"), 'w') as f:
        json.dump(analytics_db, f, indent=2)
    print("Orchestration complete. All videos and analytics saved.")

    # Convert generated videos to browser-compatible H.264 after orchestration.
    convert()

if __name__ == "__main__":
    generate()
