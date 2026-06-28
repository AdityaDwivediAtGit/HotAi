import os
import cv2
import imageio

def convert():
    video_dir = os.path.join("ui", "videos")
    for i in range(20):
        in_path = os.path.join(video_dir, f"cam_{i}.mp4")
        temp_path = os.path.join(video_dir, f"cam_{i}_temp.mp4")
        
        if not os.path.exists(in_path):
            continue
            
        print(f"Converting {in_path} to browser-compatible H.264...")
        
        try:
            cap = cv2.VideoCapture(in_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 10.0
            
            # Using imageio will automatically use ffmpeg and libx264 for perfect web compatibility
            writer = imageio.get_writer(temp_path, fps=fps, codec='libx264', macro_block_size=None)
            
            while True:
                ret, frame = cap.read()
                if not ret: break
                # Convert BGR to RGB for imageio
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                writer.append_data(frame_rgb)
                
            cap.release()
            writer.close()
            
            os.remove(in_path)
            os.rename(temp_path, in_path)
        except Exception as e:
            print(f"Error converting {in_path}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    print("All videos converted successfully!")

if __name__ == "__main__":
    convert()
