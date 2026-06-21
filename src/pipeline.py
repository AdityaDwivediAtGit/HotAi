import cv2
import json
import time
from ingestion import MockCCTV
from optical_flow import MotionExtractor
from clustering import HotspotDetector
import os
import sys

def run_pipeline(video_path, mock_gps, output_video_path, output_log_path):
    cctv = MockCCTV(video_path, mock_gps)
    extractor = MotionExtractor()
    detector = HotspotDetector(eps=40, min_samples=4)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None
    
    logs = []
    
    frame_count = 0
    while True:
        ret, frame = cctv.get_frame()
        if not ret:
            break
            
        # The extractor resizes to 640x360
        processed_frame, motion_vectors = extractor.extract_motion(frame)
        
        if out is None:
            h, w = processed_frame.shape[:2]
            out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (w, h))
            
        hotspots = detector.detect_hotspots(motion_vectors)
        
        # Visualization
        for mv in motion_vectors:
            x, y = int(mv['x']), int(mv['y'])
            dx, dy = int(mv['dx']), int(mv['dy'])
            cv2.arrowedLine(processed_frame, (x, y), (x + dx*2, y + dy*2), (0, 255, 0), 1, tipLength=0.3)
            
        current_hotspot_logs = []
        for hs in hotspots:
            cx, cy = int(hs['center_x']), int(hs['center_y'])
            density = hs['density_score']
            
            radius = min(80, density * 5)
            overlay = processed_frame.copy()
            cv2.circle(overlay, (cx, cy), radius, (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.4, processed_frame, 0.6, 0, processed_frame)
            
            cv2.circle(processed_frame, (cx, cy), radius, (0, 0, 200), 2)
            cv2.putText(processed_frame, f"Density: {density}", (cx - 20, cy - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        
            current_hotspot_logs.append({
                'timestamp': frame_count / 30.0, 
                'mock_gps': mock_gps,
                'center_x': hs['center_x'],
                'center_y': hs['center_y'],
                'density_score': density
            })
            
        if current_hotspot_logs:
            logs.extend(current_hotspot_logs)
            
        out.write(processed_frame)
        frame_count += 1
        
        # Only process first 300 frames to keep it fast
        if frame_count > 300:
            break

    cctv.release()
    if out:
        out.release()
        
    with open(output_log_path, 'w') as f:
        json.dump(logs, f, indent=2)

if __name__ == "__main__":
    import urllib.request
    
    video_file = "sample.mp4"
    if not os.path.exists(video_file):
        print("Downloading sample video...")
        try:
            # A common test video from opencv samples
            urllib.request.urlretrieve("https://github.com/intel-iot-devkit/sample-videos/raw/master/people-detection.mp4", video_file)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download video: {e}")
            sys.exit(1)
            
    mock_gps = {"lat": 40.7580, "lon": -73.9855} # Mock coordinates nearby Times Square
    
    # Save artifacts into the brain directory
    artifact_dir = r"C:\Users\dwive\.gemini\antigravity\brain\045ebdb8-4ea8-42ff-b4ad-1586e409db56"
    output_video = os.path.join(artifact_dir, "hotspot_output.mp4")
    output_log = os.path.join(artifact_dir, "hotspots_log.json")
    
    print(f"Running pipeline on {video_file}...")
    run_pipeline(video_file, mock_gps, output_video, output_log)
    print("Pipeline completed. Check the artifacts directory for outputs.")
