import cv2

class MockCCTV:
    def __init__(self, video_path, mock_gps):
        self.video_path = video_path
        self.mock_gps = mock_gps # (lat, lon)
        self.cap = cv2.VideoCapture(video_path)
    
    def get_frame(self):
        ret, frame = self.cap.read()
        return ret, frame
    
    def release(self):
        self.cap.release()
