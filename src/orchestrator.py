import cv2
import json
import os
import urllib.request
import math
import sys
from optical_flow import MotionExtractor

# Import the browser-compatibility script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from fix_videos import convert
except ImportError:
    convert = None

def get_cameras_config():
    config_path = os.path.join("src", "cameras_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
            
    # Generate rigid real-world parameters for 20 cameras around Times Square if file missing
    cameras = []
    base_lat = 40.7580
    base_lng = -73.9855
    for i in range(20):
        angle = (i / 20) * math.pi * 2
        r = 0.005 # ~500 meters away
        cameras.append({
            "id": f"Cam_{i}",
            "lat": base_lat + r * math.sin(angle),
            "lng": base_lng + r * math.cos(angle),
            "heading": math.degrees(angle + math.pi), # Strictly aligned facing center
            "fov": 90,
            "scale_pixels_to_meters": 0.05
        })
    with open(config_path, 'w') as f:
        json.dump(cameras, f, indent=2)
    return cameras

def generate():
    os.makedirs(os.path.join("ui", "videos"), exist_ok=True)
    
    base_video = "sample.mp4"
    if not os.path.exists(base_video):
        urllib.request.urlretrieve("https://github.com/intel-iot-devkit/sample-videos/raw/master/people-detection.mp4", base_video)
        
    cameras = get_cameras_config()
    analytics_db = []
    
    # PARAMETER: Heavy mode (YOLO fallback). Set True to use deep learning counting when on high-end GPU (AMD R7 M460).
    USE_HEAVY_YOLO = False 
    
    for i, cam_config in enumerate(cameras):
        print(f"Processing {cam_config['id']}...")
        cap = cv2.VideoCapture(base_video)
        
        start_frame = (i * 30) % max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        extractor = MotionExtractor(use_yolo=USE_HEAVY_YOLO)
        
        out_path = os.path.join("ui", "videos", f"cam_{i}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        
        time_series = []
        fps = 10.0 # Output virtual processing FPS
        
        # We process 100 frames to represent 10s of realtime data per camera 
        # (Clustering adds overhead, so we reduce length to ensure reasonable build times for MVP)
        for frame_idx in range(100):
            ret, _ = cap.read()
            ret, _ = cap.read()
            ret, frame = cap.read()
            if not ret or frame is None:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                
            processed_frame, people, overall_vec, dirs, unique_count = extractor.extract_motion(frame)
            
            if out is None:
                h, w = processed_frame.shape[:2]
                out = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
                
            out.write(processed_frame)
            
            # Record Exact Frame-by-Frame Analytics Data for UI Synchronization
            timestamp = round(frame_idx / fps, 2)
            time_series.append({
                "time": timestamp,
                "counts": dirs.copy(),
                "total": unique_count,
                "dominant_vector_dx": float(overall_vec[0]) if not math.isnan(overall_vec[0]) else 0,
                "dominant_vector_dy": float(overall_vec[1]) if not math.isnan(overall_vec[1]) else 0
            })
            
        out.release()
        cap.release()
        
        cam_analytics = cam_config.copy()
        cam_analytics["video_path"] = f"videos/cam_{i}.mp4"
        cam_analytics["time_series"] = time_series
        analytics_db.append(cam_analytics)
        
    with open(os.path.join("ui", "camera_analytics.json"), 'w') as f:
        json.dump(analytics_db, f, indent=2)
        
    print("Orchestration complete.")
    if convert:
        print("Initiating browser-compatibility conversion...")
        convert()
    else:
        print("fix_videos.py not found. Skipping web conversion.")

if __name__ == "__main__":
    generate()
