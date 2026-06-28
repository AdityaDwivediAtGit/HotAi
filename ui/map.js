let map;
let cameras = [];
let hotspotsLayer;
let trajectoriesLayer;
let rawVectors = [];

const MAP_CENTER = [40.7580, -73.9855]; // Times Square

function initMap() {
    map = L.map('map', {
        zoomControl: false 
    }).setView(MAP_CENTER, 15);
    
    // Dark mode CARTO tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a>'
    }).addTo(map);

    hotspotsLayer = L.layerGroup().addTo(map);
    trajectoriesLayer = L.layerGroup().addTo(map);

    fetchData();
}

async function fetchData() {
    try {
        const response = await fetch('raw_vectors.json');
        rawVectors = await response.json();
        
        // If empty or failed, generate mock vectors
        if (!rawVectors || rawVectors.length === 0) {
            generateMockVectors();
        }
        setupCameras();
    } catch (e) {
        console.warn("Could not load vectors, generating mock vectors", e);
        generateMockVectors();
        setupCameras();
    }
}

function generateMockVectors() {
    rawVectors = [];
    for(let i=0; i<30; i++) {
        rawVectors.push({dx: Math.random()*2+1, dy: Math.random()*2+1});
    }
}

function setupCameras() {
    const radius = 0.005; // Roughly 500 meters
    const numCameras = 20;
    
    for (let i = 0; i < numCameras; i++) {
        const angle = (i / numCameras) * Math.PI * 2;
        const r = radius + (Math.random() * 0.002 - 0.001);
        
        const lat = MAP_CENTER[0] + r * Math.sin(angle);
        const lng = MAP_CENTER[1] + r * Math.cos(angle);
        
        const marker = L.marker([lat, lng], { draggable: true }).addTo(map);
        marker.on('dragend', calculateConvergence);
        marker.on('mouseover', (e) => handleMarkerHover(i, true, e));
        marker.on('mouseout', (e) => handleMarkerHover(i, false, e));
        // Click pins/unpins the camera preview instead of opening a file dialog
        marker.on('click', () => togglePinMarker(i));

        cameras.push({
            id: 'Cam_' + i,
            marker: marker,
            video: '../sample.mp4', // default footage (relative path)
            pinned: false
        });
    }
    
    calculateConvergence();
}

// Hover preview handling
const previewEl = document.getElementById('hover-preview');
const previewVideo = document.getElementById('hover-video');
const previewTitle = document.getElementById('preview-title');
const previewStats = document.getElementById('preview-stats');
const pinBtn = document.getElementById('pin-btn');
const assignBtn = document.getElementById('assign-btn');
const fileInput = document.getElementById('file-input');

function handleMarkerHover(index, entering, event) {
    const cam = cameras[index];
    if (!cam) return;

    if (entering) {
        // Populate preview
        previewTitle.innerText = cam.id;
        const info = computeCameraStats(cam);
        previewStats.innerText = `Vectors: ${info.count} • Avg speed: ${info.avg.toFixed(2)}`;
        // Set video source
        try {
            previewVideo.pause();
            previewVideo.src = cam.video || '../sample.mp4';
            previewVideo.currentTime = 0;
            previewVideo.play().catch(()=>{});
        } catch (e) {}

        // Position preview near marker and show it unless another camera is pinned
        if (!isAnyPinned() || cam.pinned) {
            positionPreviewNearMarker(cam, event);
            showPreview();
        }
    } else {
        // Hide preview unless this camera is pinned
        if (!cam.pinned) {
            // find any other pinned camera
            if (!isAnyPinned()) hidePreview();
        }
    }
}

function positionPreviewNearMarker(cam, event) {
    // Determine a container point for the marker (use event.latlng if available)
    let latlng = cam.marker.getLatLng();
    if (event && event.latlng) latlng = event.latlng;

    const containerPoint = map.latLngToContainerPoint(latlng);
    const rect = map.getContainer().getBoundingClientRect();
    const absX = Math.round(rect.left + containerPoint.x);
    const absY = Math.round(rect.top + containerPoint.y);

    // Place preview to the right of the marker by default
    const offsetX = 20;
    const offsetY = -40;

    // Apply to preview element
    previewEl.style.left = (absX + offsetX) + 'px';
    // Try to vertically center preview around marker
    const approxTop = absY + offsetY - (previewEl.offsetHeight / 2 || 0);
    // Clamp to viewport
    const maxTop = window.innerHeight - previewEl.offsetHeight - 10;
    const topVal = Math.max(10, Math.min(maxTop, approxTop));
    previewEl.style.top = topVal + 'px';
}

function showPreview() { previewEl.classList.remove('hidden'); }
function hidePreview() { previewEl.classList.add('hidden'); previewVideo.pause(); }

function isAnyPinned() { return cameras.some(c=>c.pinned); }

pinBtn.addEventListener('click', () => {
    // Toggle pin on the currently visible camera (by title)
    const id = previewTitle.innerText;
    const cam = cameras.find(c=>c.id === id);
    if (!cam) return;
    cam.pinned = !cam.pinned;
    pinBtn.classList.toggle('active', cam.pinned);
    pinBtn.innerText = cam.pinned ? 'Unpin' : 'Pin';
});

assignBtn.addEventListener('click', () => {
    fileInput.value = null;
    fileInput.click();
});

fileInput.addEventListener('change', (ev) => {
    const files = ev.target.files;
    if (!files || files.length === 0) return;
    const file = files[0];
    const url = URL.createObjectURL(file);
    // assign to current preview camera
    const id = previewTitle.innerText;
    const cam = cameras.find(c=>c.id === id);
    if (!cam) return;
    cam.video = url;
    // immediately play
    previewVideo.pause();
    previewVideo.src = url;
    previewVideo.play().catch(()=>{});
});

function openAssignDialog(index) {
    const cam = cameras[index];
    if (!cam) return;
    // open file chooser to assign footage
    previewTitle.innerText = cam.id;
    previewStats.innerText = 'Click Assign Footage to choose a local video file.';
    fileInput.value = null;
    fileInput.click();
}

function togglePinMarker(index) {
    const cam = cameras[index];
    if (!cam) return;
    cam.pinned = !cam.pinned;

    // If pinning, show and populate preview for this camera
    previewTitle.innerText = cam.id;
    const info = computeCameraStats(cam);
    previewStats.innerText = `Vectors: ${info.count} • Avg speed: ${info.avg.toFixed(2)}`;
    try {
        previewVideo.pause();
        previewVideo.src = cam.video || '../sample.mp4';
        previewVideo.currentTime = 0;
        previewVideo.play().catch(()=>{});
    } catch (e) {}

    // Update preview visibility and pin button state
    if (cam.pinned) {
        showPreview();
        pinBtn.classList.add('active');
        pinBtn.innerText = 'Unpin';
    } else {
        pinBtn.classList.remove('active');
        pinBtn.innerText = 'Pin';
        // If no other camera pinned, hide preview
        if (!isAnyPinned()) hidePreview();
    }
}

function computeCameraStats(cam) {
    // Compute simple stats from rawVectors: count and avg magnitude
    const count = rawVectors.length;
    let sum = 0;
    for (let v of rawVectors) sum += Math.sqrt(v.dx*v.dx + v.dy*v.dy);
    const avg = count ? (sum / count) : 0;
    return { count, avg };
}

// Simple DBSCAN in JS for Geographic coordinates
function dbscan(points, eps, minPts) {
    let labels = new Array(points.length).fill(0);
    let clusterId = 0;
    
    function getDistance(p1, p2) {
        const dx = p1.lat - p2.lat;
        const dy = p1.lng - p2.lng;
        return Math.sqrt(dx*dx + dy*dy);
    }

    for (let i = 0; i < points.length; i++) {
        if (labels[i] !== 0) continue;
        
        let neighbors = [];
        for (let j = 0; j < points.length; j++) {
            if (getDistance(points[i], points[j]) <= eps) neighbors.push(j);
        }
        
        if (neighbors.length < minPts) {
            labels[i] = -1; 
        } else {
            clusterId++;
            labels[i] = clusterId;
            let seedSet = [...neighbors];
            
            for (let j = 0; j < seedSet.length; j++) {
                let q = seedSet[j];
                if (labels[q] === -1) labels[q] = clusterId;
                if (labels[q] !== 0) continue;
                labels[q] = clusterId;
                
                let qNeighbors = [];
                for (let k = 0; k < points.length; k++) {
                    if (getDistance(points[q], points[k]) <= eps) qNeighbors.push(k);
                }
                
                if (qNeighbors.length >= minPts) {
                    for(let k=0; k<qNeighbors.length; k++) {
                        if(!seedSet.includes(qNeighbors[k])) seedSet.push(qNeighbors[k]);
                    }
                }
            }
        }
    }
    
    let clusters = {};
    for (let i = 0; i < points.length; i++) {
        let cid = labels[i];
        if (cid > 0) {
            if (!clusters[cid]) clusters[cid] = [];
            clusters[cid].push(points[i]);
        }
    }
    return Object.values(clusters);
}

function calculateConvergence() {
    hotspotsLayer.clearLayers();
    trajectoriesLayer.clearLayers();
    
    let projectedPoints = [];
    const scaleFactor = 0.0001; 
    
    cameras.forEach(cam => {
        const latLng = cam.marker.getLatLng();
        const angleToCenter = Math.atan2(MAP_CENTER[0] - latLng.lat, MAP_CENTER[1] - latLng.lng);
        
        rawVectors.forEach(v => {
            const magnitude = Math.sqrt(v.dx*v.dx + v.dy*v.dy);
            const noise = (Math.random() - 0.5) * 0.4; // 0.4 radians noise ~ 22 degrees
            const finalAngle = angleToCenter + noise;
            
            const noisyMag = magnitude * (0.5 + Math.random());
            
            const projLat = latLng.lat + (Math.sin(finalAngle) * noisyMag * scaleFactor);
            const projLng = latLng.lng + (Math.cos(finalAngle) * noisyMag * scaleFactor);
            
            projectedPoints.push({
                lat: projLat,
                lng: projLng,
                source: cam.id
            });
            
            // Render 10% of trajectories for performance/visual clarity
            if(Math.random() > 0.9) {
                L.polyline([[latLng.lat, latLng.lng], [projLat, projLng]], {
                    color: 'rgba(56, 189, 248, 0.2)',
                    weight: 1
                }).addTo(trajectoriesLayer);
            }
        });
    });
    
    const clusters = dbscan(projectedPoints, 0.0015, 8);
    let hotspotCount = 0;
    
    clusters.forEach(cluster => {
        if (cluster.length < 20) return; // Only show significant clusters
        hotspotCount++;
        
        let sumLat = 0; let sumLng = 0;
        cluster.forEach(p => { sumLat += p.lat; sumLng += p.lng; });
        const centerLat = sumLat / cluster.length;
        const centerLng = sumLng / cluster.length;
        
        // Probability determines color
        const prob = Math.min(1.0, cluster.length / 100.0);
        const r = 255;
        const g = Math.floor(255 * (1 - prob));
        const color = `rgb(${r}, ${g}, 0)`;
        
        L.circle([centerLat, centerLng], {
            color: color,
            fillColor: color,
            fillOpacity: 0.6,
            radius: 60 + (prob * 100)
        }).addTo(hotspotsLayer);
    });
    
    document.getElementById('hotspot-count').innerText = hotspotCount;
}

window.recalculate = calculateConvergence;
window.onload = initMap;
