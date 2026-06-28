# HotAI MVP

HotAI is an intelligent video processing pipeline that detects spatial hotspots and anomalies in CCTV footage. It tracks motion vectors from pedestrians or moving objects and uses DBSCAN clustering to identify dense spots (e.g., crowd convergence) in real-time.

## Features
- **Mock CCTV Ingestion**: Streams mock or actual `.mp4` CCTV footage and maps it to a designated GPS coordinate.
- **Fast Optical Flow**: Uses OpenCV and Lucas-Kanade tracking on Shi-Tomasi corners to rapidly extract motion vectors (magnitude and direction).
- **Spatial Density Clustering**: Utilizes DBSCAN (Density-Based Spatial Clustering of Applications with Noise) via `scikit-learn` to cluster moving entities into identifiable hotspots based on density.
- **Artifact Output**: Automatically generates a processed `.mp4` video with visual heatmap overlays highlighting hotspot clusters and outputting JSON logs tracking density and timestamp information.

## Project Structure
- `.agents/` and `agent.yaml`: Configures the internal multi-agent architecture defining roles (`VisionCoder` and `AnalyticsCoder`).
- `src/ingestion.py`: Contains the `MockCCTV` class for loading video feeds.
- `src/optical_flow.py`: Contains the `MotionExtractor` class for generating motion vectors.
- `src/clustering.py`: Contains the `HotspotDetector` class for running DBSCAN clustering.
- `src/pipeline.py`: The overarching pipeline logic that links ingestion, motion extraction, and clustering to generate final artifacts.
- `requirements.txt`: Python package dependencies.

## Installation

Ensure you have Python 3.7+ installed.

1. Navigate to the project root directory.
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main pipeline script. By default, this will download a sample CCTV tracking video (`people-detection.mp4`), run the hotspot detection, and output the results.

```bash
python src/pipeline.py
```

### Outputs
After running the script, the artifacts will be saved to your configured output path (by default, in the generated workspace `artifacts/` directory):

- **`artifacts/hotspot_output.mp4`**: A video overlay containing red circles acting as heatmaps on areas with high motion density.
- **`artifacts/hotspots_log.json`**: A JSON document logging the mock GPS coordinates, timestamps, cluster centers, and density scores for each detected hotspot.

You can open the output video with your preferred media player or inspect the JSON with any editor.

### Running Tests
Run the automated test suite from the project root:

```bash
python -m unittest tests.test_hotai
```

For verbose output:

```bash
python -m unittest tests.test_hotai -v
```
