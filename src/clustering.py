import numpy as np
from sklearn.cluster import DBSCAN

class HotspotDetector:
    def __init__(self, eps=40, min_samples=3):
        self.dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        
    def detect_hotspots(self, motion_vectors):
        if not motion_vectors or len(motion_vectors) < self.dbscan.min_samples:
            return []
            
        # Extract coordinates for clustering
        points = np.array([[mv['x'], mv['y']] for mv in motion_vectors])
        
        # Cluster the points based on spatial density
        labels = self.dbscan.fit_predict(points)
        
        hotspots = []
        unique_labels = set(labels)
        
        for label in unique_labels:
            if label == -1:
                continue # Noise
                
            cluster_points = points[labels == label]
            density_score = len(cluster_points)
            
            # Hotspot center
            center_x = np.mean(cluster_points[:, 0])
            center_y = np.mean(cluster_points[:, 1])
            
            hotspots.append({
                'label': int(label),
                'center_x': float(center_x),
                'center_y': float(center_y),
                'density_score': density_score,
                'points': cluster_points.tolist()
            })
            
        return hotspots
