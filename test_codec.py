import cv2
import numpy as np
import os

def test():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Test WebM (VP8)
    out1 = cv2.VideoWriter('test.webm', cv2.VideoWriter_fourcc(*'vp80'), 10, (100, 100))
    if out1.isOpened():
        out1.write(frame)
        out1.release()
        print("VP8 (WebM) Supported!")
    else:
        print("VP8 Not Supported")

    # Test AVC1 (H264)
    out2 = cv2.VideoWriter('test_avc1.mp4', cv2.VideoWriter_fourcc(*'avc1'), 10, (100, 100))
    if out2.isOpened():
        out2.write(frame)
        out2.release()
        print("AVC1 Supported!")
    else:
        print("AVC1 Not Supported")

if __name__ == "__main__":
    test()
