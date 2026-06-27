import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the package sources are importable when tests run from the repo root.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import cv2
import numpy as np

from ingestion import MockCCTV
from optical_flow import MotionExtractor
from clustering import HotspotDetector
from pipeline import run_pipeline


def create_synthetic_video(path, frame_count=60, width=320, height=240):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(path), fourcc, 30.0, (width, height))
    for i in range(frame_count):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        x = int((width - 40) * (i / max(frame_count - 1, 1)))
        y = height // 2 - 20
        cv2.rectangle(frame, (x, y), (x + 40, y + 40), (255, 255, 255), -1)
        out.write(frame)
    out.release()
    assert os.path.exists(path), f"Synthetic video was not written to {path}"
    return path


class TestHotAi(unittest.TestCase):
    def test_mock_cctv_reads_frames(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test_video.mp4"
            create_synthetic_video(video_path)

            cctv = MockCCTV(str(video_path), mock_gps={"lat": 0.0, "lon": 0.0})
            ret, frame = cctv.get_frame()
            cctv.release()

            self.assertTrue(ret)
            self.assertIsNotNone(frame)
            self.assertEqual(frame.shape[2], 3)

    def test_motion_extractor_returns_vectors_for_moving_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "moving_video.mp4"
            create_synthetic_video(video_path, frame_count=10, width=320, height=240)

            extractor = MotionExtractor()
            cap = cv2.VideoCapture(str(video_path))
            ret, frame = cap.read()
            self.assertTrue(ret)
            frame1, vectors1 = extractor.extract_motion(frame)
            self.assertEqual(len(vectors1), 0)

            ret, frame = cap.read()
            self.assertTrue(ret)
            frame2, vectors2 = extractor.extract_motion(frame)
            cap.release()

            self.assertGreaterEqual(len(vectors2), 0)
            self.assertIsInstance(frame2, np.ndarray)
            if len(vectors2) > 0:
                self.assertIn("x", vectors2[0])
                self.assertIn("dx", vectors2[0])
                self.assertIn("magnitude", vectors2[0])

    def test_hotspot_detector_groups_motion_vectors(self):
        vectors = [
            {"x": 10 + i, "y": 10, "dx": 1.0, "dy": 0.0, "magnitude": 1.5, "angle": 0.0}
            for i in range(5)
        ] + [
            {"x": 100 + i, "y": 100, "dx": 1.0, "dy": 0.0, "magnitude": 1.5, "angle": 0.0}
            for i in range(5)
        ]

        detector = HotspotDetector(eps=20, min_samples=3)
        hotspots = detector.detect_hotspots(vectors)

        self.assertEqual(len(hotspots), 2)
        self.assertTrue(all("center_x" in hs and "center_y" in hs for hs in hotspots))
        self.assertTrue(all(hs["density_score"] >= 3 for hs in hotspots))

    def test_run_pipeline_produces_video_and_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "source.mp4"
            output_video = Path(tmpdir) / "hotspot_output.mp4"
            output_log = Path(tmpdir) / "hotspots_log.json"

            create_synthetic_video(video_path, frame_count=30, width=320, height=240)
            mock_gps = {"lat": 40.0, "lon": -74.0}

            run_pipeline(str(video_path), mock_gps, str(output_video), str(output_log))

            self.assertTrue(output_video.exists())
            self.assertTrue(output_log.exists())

            cap = cv2.VideoCapture(str(output_video))
            self.assertTrue(cap.isOpened())
            ret, frame = cap.read()
            cap.release()
            self.assertTrue(ret)
            self.assertIsNotNone(frame)

            with open(output_log, "r", encoding="utf-8") as f:
                import json
                logs = json.load(f)

            self.assertIsInstance(logs, list)
            if logs:
                self.assertIn("timestamp", logs[0])
                self.assertIn("mock_gps", logs[0])
                self.assertEqual(logs[0]["mock_gps"], mock_gps)


if __name__ == "__main__":
    unittest.main()
