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
        
        cameras.push({
            id: 'Cam_' + i,
            marker: marker
        });
    }
    
    calculateConvergence();
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
