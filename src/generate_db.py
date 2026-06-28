import cv2
import json
import os
from ingestion import MockCCTV
from optical_flow import MotionExtractor

def generate():
    video_file = "sample.mp4"
    if not os.path.exists(video_file):
        print("Missing sample.mp4")
        return
        
    cctv = MockCCTV(video_file, None)
    extractor = MotionExtractor()
    
    all_vectors = []
    
    # Extract from 50 frames to get a good sample of walking vectors
    for i in range(50):
        ret, frame = cctv.get_frame()
        if not ret: break
        
        _, motion_vectors = extractor.extract_motion(frame)
        
        # We just want the raw (dx, dy) displacements, normalized
        for mv in motion_vectors:
            # only keep vectors that represent significant motion
            if mv['magnitude'] > 2.0:
                all_vectors.append({
                    'dx': mv['dx'],
                    'dy': mv['dy']
                })
                
    cctv.release()
    
    # Save to UI folder
    out_path = os.path.join("ui", "raw_vectors.json")
    with open(out_path, 'w') as f:
        json.dump(all_vectors, f)
        
    print(f"Exported {len(all_vectors)} raw motion vectors to {out_path}")

if __name__ == "__main__":
    generate()
