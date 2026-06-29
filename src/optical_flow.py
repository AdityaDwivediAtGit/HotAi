import cv2
import numpy as np
import math
from sklearn.cluster import DBSCAN

class MotionExtractor:
    def __init__(self, use_yolo=False):
        self.use_yolo = use_yolo
        self.prev_gray = None
        self.feature_params = dict(maxCorners=300, qualityLevel=0.1, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.p0 = None
        
        # Heavy YOLO model setup (Optional fallback)
        self.yolo_model = None
        if self.use_yolo:
            try:
                from ultralytics import YOLO
                print("Loading Heavy YOLO Model...")
                self.yolo_model = YOLO("yolov8n.pt") 
            except ImportError:
                print("Ultralytics not installed. Falling back to lightweight clustering.")
                self.use_yolo = False

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
        
        direction_counts = {"North": 0, "South": 0, "East": 0, "West": 0}
        unique_people = 0
        
        if self.use_yolo and self.yolo_model:
            # HEAVY MODE: YOLO Object Detection
            results = self.yolo_model(frame, classes=[0], verbose=False)
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                direction_counts["North"] += 1 
                unique_people += 1
            return frame, [], (0, 0), direction_counts, unique_people
            
        # LIGHTWEIGHT MODE: Optical Flow + Spatial DBSCAN Clustering
        overall_dx, overall_dy = 0, 0
        raw_vectors = []
        
        if self.prev_gray is None:
            self.prev_gray = gray
            self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return frame, [], (0, 0), direction_counts, 0
            
        if self.p0 is not None and len(self.p0) > 0:
            p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.p0, None, **self.lk_params)
            if p1 is not None:
                good_new = p1[st == 1]
                good_old = self.p0[st == 1]
                
                for new, old in zip(good_new, good_old):
                    a, b = new.ravel()
                    c, d = old.ravel()
                    dx = float(a - c)
                    dy = float(b - d)
                    
                    if np.sqrt(dx**2 + dy**2) > 1.0:
                        raw_vectors.append([float(a), float(b), dx, dy])
                        
            if len(good_new) < 50:
                self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            else:
                self.p0 = good_new.reshape(-1, 1, 2)
        else:
            self.p0 = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            
        self.prev_gray = gray
        
        # CLUSTERING: Group raw points to count unique physical people
        clustered_people = []
        if len(raw_vectors) > 0:
            points = np.array([[v[0], v[1]] for v in raw_vectors])
            # Group points moving within a 40 pixel radius (person-sized box)
            clustering = DBSCAN(eps=40, min_samples=1).fit(points)
            labels = clustering.labels_
            
            for cluster_id in set(labels):
                if cluster_id == -1: continue
                cluster_indices = [i for i, lbl in enumerate(labels) if lbl == cluster_id]
                cluster_vectors = [raw_vectors[i] for i in cluster_indices]
                
                # Average position and direction of the single person
                avg_x = sum(v[0] for v in cluster_vectors) / len(cluster_vectors)
                avg_y = sum(v[1] for v in cluster_vectors) / len(cluster_vectors)
                avg_dx = sum(v[2] for v in cluster_vectors) / len(cluster_vectors)
                avg_dy = sum(v[3] for v in cluster_vectors) / len(cluster_vectors)
                
                clustered_people.append((avg_x, avg_y, avg_dx, avg_dy))
                overall_dx += avg_dx
                overall_dy += avg_dy
                
                # Render Individual Person Tracking Arrow
                cv2.arrowedLine(frame, (int(avg_x), int(avg_y)), (int(avg_x + avg_dx*4), int(avg_y + avg_dy*4)), (0, 0, 255), 2, tipLength=0.3)
                # Render Person Bounding Circle
                cv2.circle(frame, (int(avg_x), int(avg_y)), 15, (255, 0, 0), 1)
                
                dir_str = self.get_direction(avg_dx, avg_dy)
                direction_counts[dir_str] += 1
                unique_people += 1

        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        if unique_people > 0:
            overall_dx /= unique_people
            overall_dy /= unique_people
            
            if abs(overall_dx) > 0.5 or abs(overall_dy) > 0.5:
                cv2.arrowedLine(frame, (center_x, center_y), (int(center_x + overall_dx*15), int(center_y + overall_dy*15)), (0, 255, 0), 4, tipLength=0.3)
                cv2.putText(frame, "CROWD FLOW", (center_x - 50, center_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
        return frame, clustered_people, (overall_dx, overall_dy), direction_counts, unique_people
