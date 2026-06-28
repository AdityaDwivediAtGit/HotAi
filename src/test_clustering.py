import unittest
from clustering import HotspotDetector

class TestClustering(unittest.TestCase):
    def test_predictive_convergence(self):
        detector = HotspotDetector(eps=500, min_samples=3, projection_frames=100)
        
        # Mock motion vectors from multiple sources
        # Video 1: 3 people at (0, 0) moving towards (1000, 1000)
        # Vector step per frame = (10, 10)
        v1_vectors = [{'source_id': 'Video 1', 'x': 0, 'y': 0, 'dx': 10, 'dy': 10} for _ in range(3)]
        
        # Point B: 5 people at (2000, 0) moving towards (1000, 1000)
        # Vector step per frame = (-10, 10)
        pb_vectors = [{'source_id': 'Point B', 'x': 2000, 'y': 0, 'dx': -10, 'dy': 10} for _ in range(5)]
        
        # Point D: 7 people at (1000, 2000) moving towards (1000, 1000)
        # Vector step per frame = (0, -10)
        pd_vectors = [{'source_id': 'Point D', 'x': 1000, 'y': 2000, 'dx': 0, 'dy': -10} for _ in range(7)]
        
        all_vectors = v1_vectors + pb_vectors + pd_vectors
        
        hotspots = detector.detect_hotspots(all_vectors)
        
        self.assertEqual(len(hotspots), 1, "Should detect exactly one convergence hotspot")
        hotspot = hotspots[0]
        
        # With 100 frames of projection, all groups arrive at (1000, 1000)
        self.assertAlmostEqual(hotspot['projected_center_x'], 1000)
        self.assertAlmostEqual(hotspot['projected_center_y'], 1000)
        self.assertEqual(hotspot['density_score'], 15)
        self.assertEqual(set(hotspot['unique_sources']), {'Video 1', 'Point B', 'Point D'})
        self.assertTrue(hotspot['probability'] > 0)

if __name__ == '__main__':
    unittest.main()
