import cv2
import numpy as np

class MotionExtractor:
    def __init__(self):
        self.prev_gray = None
        self.feature_params = dict(maxCorners=200, qualityLevel=0.1, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.p0 = None

    def extract_motion(self, frame):
        # Resize to process faster and normalize sizes
        frame = cv2.resize(frame, (640, 360))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        motion_vectors = []
        
        if self.prev_gray is None:
            self.prev_gray = gray
            self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return frame, motion_vectors
            
        if self.p0 is not None and len(self.p0) > 0:
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.p0, None, **self.lk_params)
            
            if p1 is not None:
                good_new = p1[st == 1]
                good_old = self.p0[st == 1]
                
                for i, (new, old) in enumerate(zip(good_new, good_old)):
                    a, b = new.ravel()
                    c, d = old.ravel()
                    
                    dx = a - c
                    dy = b - d
                    magnitude = np.sqrt(dx**2 + dy**2)
                    angle = np.arctan2(dy, dx)
                    
                    # only keep significant motion
                    if magnitude > 1.0:
                        motion_vectors.append({
                            'x': float(a), 'y': float(b),
                            'dx': float(dx), 'dy': float(dy),
                            'magnitude': float(magnitude),
                            'angle': float(angle)
                        })
            
            # Update points if they are too few
            if len(good_new) < 20:
                self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            else:
                self.p0 = good_new.reshape(-1, 1, 2)
        else:
            self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            
        self.prev_gray = gray
        return frame, motion_vectors
