# Predictive Hotspot Detection via Trajectory Convergence

This document outlines the proposed implementation to enhance our hotspot detection logic by predicting crowd convergence based on movement trajectories. 

## Goal Description
Currently, the system flags hotspots based purely on the current spatial density of moving objects. This enhancement will project the motion vectors (trajectories) forward in time. By clustering the *projected* future locations of moving entities, the system will identify "potential hotspots" where people from various origins (e.g., Point B, Point C, Point D) are converging towards a single destination (Point A).

## Proposed Changes

### [MODIFY] [clustering.py](file:///c:/Users/dwive/OneDrive/Documents/Git%20Cloned/HotAi/src/clustering.py)
- Introduce a `projection_factor` (e.g., predicting `N` frames into the future).
- For each motion vector, calculate a projected destination: `projected_x = x + (dx * projection_factor)`.
- Apply DBSCAN clustering on these *projected coordinates* rather than the current coordinates.
- Return these projected hotspots, differentiating them as "Convergence Zones".

### [MODIFY] [pipeline.py](file:///c:/Users/dwive/OneDrive/Documents/Git%20Cloned/HotAi/src/pipeline.py)
- Update the visualization logic to draw the predicted convergence zones (perhaps in a different color, like orange or yellow, to distinguish them from current density hotspots).
- Draw lines indicating the projected paths of moving objects towards these convergence zones.
- Update the JSON log schema to include the `predicted_convergence_x` and `predicted_convergence_y`.

## Open Questions

> [!IMPORTANT]
> 1. **Projection Timeframe**: How far into the future should the system project? For the MVP, I propose projecting 30 to 60 frames ahead (1 to 2 seconds). We can adjust this multiplier if you need longer-term predictions. 
> 2. **Visualization**: I propose drawing yellow glowing circles for "Future Convergence Zones" and keeping red circles for "Current High Density". Does this coloring scheme work for you?
> 3. **Mock Multi-Camera Context**: In the current MVP, we process a single video stream and calculate convergence within its frame. Do you want me to write the logic such that it easily accepts arrays of vectors from *multiple* cameras (e.g., adding a `source_id` to each vector) for future scalability?

## Verification Plan
### Automated Tests
- N/A for MVP script structure.

### Manual Verification
- Re-run `src/pipeline.py` on the sample video.
- Observe the output video artifact: It should now display yellow convergence zones where paths intersect, projecting where the crowd will be.
- Verify the JSON log contains the new predicted coordinates.
