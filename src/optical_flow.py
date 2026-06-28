import cv2
import numpy as np
import math

class MotionExtractor:
    def __init__(self):
        self.prev_gray = None
        self.feature_params = dict(maxCorners=200, qualityLevel=0.1, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.p0 = None
        self.history_dx = []
        self.history_dy = []

    def get_direction(self, dx, dy):
        angle = math.degrees(math.atan2(dy, dx))
        if angle < 0: angle += 360
        if 45 <= angle < 135: return "South"
        if 135 <= angle < 225: return "West"
        if 225 <= angle < 315: return "North"
        return "East"

    def extract_motion(self, frame):
        frame = cv2.resize(frame, (640, 360))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        motion_vectors = []
        overall_dx, overall_dy = 0, 0
        direction_counts = {"North": 0, "South": 0, "East": 0, "West": 0}
        
        if self.prev_gray is None:
            self.prev_gray = gray
            self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return frame, motion_vectors, (0, 0), direction_counts
            
        if self.p0 is not None and len(self.p0) > 0:
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.p0, None, **self.lk_params)
            
            if p1 is not None:
                good_new = p1[st == 1]
                good_old = self.p0[st == 1]
                
                for i, (new, old) in enumerate(zip(good_new, good_old)):
                    a, b = new.ravel()
                    c, d = old.ravel()
                    
                    dx = float(a - c)
                    dy = float(b - d)
                    magnitude = np.sqrt(dx**2 + dy**2)
                    
                    if magnitude > 1.0:
                        motion_vectors.append({'x': float(a), 'y': float(b), 'dx': dx, 'dy': dy})
                        overall_dx += dx
                        overall_dy += dy
                        
                        # Draw individual arrow (Red)
                        cv2.arrowedLine(frame, (int(c), int(d)), (int(a + dx*3), int(b + dy*3)), (0, 0, 255), 2, tipLength=0.4)
                        
                        direction = self.get_direction(dx, dy)
                        direction_counts[direction] += 1
            
            if len(good_new) < 20:
                self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            else:
                self.p0 = good_new.reshape(-1, 1, 2)
        else:
            self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            
        self.prev_gray = gray
        
        if len(motion_vectors) > 0:
            avg_dx = overall_dx / len(motion_vectors)
            avg_dy = overall_dy / len(motion_vectors)
            self.history_dx.append(avg_dx)
            self.history_dy.append(avg_dy)
            if len(self.history_dx) > 10:
                self.history_dx.pop(0)
                self.history_dy.pop(0)
        
        smooth_dx = sum(self.history_dx)/len(self.history_dx) if self.history_dx else 0
        smooth_dy = sum(self.history_dy)/len(self.history_dy) if self.history_dy else 0
        
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        if abs(smooth_dx) > 0.5 or abs(smooth_dy) > 0.5:
            cv2.arrowedLine(frame, (center_x, center_y), (int(center_x + smooth_dx*20), int(center_y + smooth_dy*20)), (0, 255, 0), 4, tipLength=0.3)
            cv2.putText(frame, "OVERALL CROWD FLOW", (center_x - 80, center_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        return frame, motion_vectors, (smooth_dx, smooth_dy), direction_counts
