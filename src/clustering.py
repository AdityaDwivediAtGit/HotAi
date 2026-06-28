import numpy as np
from sklearn.cluster import DBSCAN

class HotspotDetector:
    def __init__(self, eps=40, min_samples=3, projection_frames=54000):
        # eps defines how close projected points need to be to form a convergence zone
        self.dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        self.projection_frames = projection_frames
        
    def detect_hotspots(self, motion_vectors):
        if not motion_vectors or len(motion_vectors) < self.dbscan.min_samples:
            return []
            
        # Extract and project coordinates for clustering
        points = []
        for mv in motion_vectors:
            # Project trajectory into the future
            proj_x = mv['x'] + (mv['dx'] * self.projection_frames)
            proj_y = mv['y'] + (mv['dy'] * self.projection_frames)
            points.append([proj_x, proj_y])
            
        points = np.array(points)
        
        # Cluster the projected points based on spatial density
        labels = self.dbscan.fit_predict(points)
        
        hotspots = []
        unique_labels = set(labels)
        
        for label in unique_labels:
            if label == -1:
                continue # Noise
                
            cluster_indices = np.where(labels == label)[0]
            cluster_points = points[cluster_indices]
            density_score = len(cluster_points)
            
            # Identify unique sources contributing to this hotspot
            sources = set()
            for idx in cluster_indices:
                mv = motion_vectors[idx]
                if 'source_id' in mv:
                    sources.add(mv['source_id'])
            
            # Hotspot center
            center_x = np.mean(cluster_points[:, 0])
            center_y = np.mean(cluster_points[:, 1])
            
            # Probability calculation (normalized up to a max expected density of 20)
            probability = min(1.0, density_score / 20.0)
            
            hotspots.append({
                'label': int(label),
                'projected_center_x': float(center_x),
                'projected_center_y': float(center_y),
                'density_score': density_score,
                'probability': probability,
                'unique_sources': list(sources),
                'points': cluster_points.tolist()
            })
            
        return hotspots
