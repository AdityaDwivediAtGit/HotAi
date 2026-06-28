let map;
let cameras = [];
let hotspotsLayer;
let trajectoriesLayer;
let analyticsDB = [];

const MAP_CENTER = [40.7580, -73.9855];
const BASE_ASSET_URL = new URL('.', window.location.href).href;

function initMap() {
    map = L.map('map', { zoomControl: false }).setView(MAP_CENTER, 15);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CARTO'
    }).addTo(map);

    hotspotsLayer = L.layerGroup().addTo(map);
    trajectoriesLayer = L.layerGroup().addTo(map);

    fetchData();
}

async function fetchData() {
    const analyticsUrl = new URL('camera_analytics.json', BASE_ASSET_URL).href;
    try {
        console.log('Fetching analytics from', analyticsUrl);
        const response = await fetch(analyticsUrl);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        analyticsDB = await response.json();
        setupCameras();
    } catch (e) {
        console.warn('Unable to load camera_analytics.json:', e);
        alert('Unable to load camera analytics. Please ensure camera_analytics.json is available in the UI folder and that the page is served from a web server.');
    }
}

function setupCameras() {
    analyticsDB.forEach((camData, i) => {
        // Use coordinates from JSON initially, but allow dragging
        const marker = L.marker([camData.lat, camData.lng], { draggable: true }).addTo(map);
        
        marker.on('dragend', calculateConvergence);
        marker.on('click', () => openPanel(i));
        
        cameras.push({
            id: camData.id,
            marker: marker,
            data: camData
        });
    });
    calculateConvergence();
}

function openPanel(index) {
    const cam = cameras[index].data;
    document.getElementById('cam-title').innerText = cam.id + " Analytics";
    
    // Resolve video URL from the same asset folder as the script
    const videoElem = document.getElementById('cam-video');
    const sourceElem = videoElem.querySelector('source');
    const videoUrl = new URL(cam.video_path, BASE_ASSET_URL).href;
    console.log('Loading camera video:', videoUrl);

    videoElem.onerror = (ev) => {
        console.error('Video element error for', videoUrl, ev);
    };
    sourceElem.onerror = () => {
        console.error('Video source failed to load:', videoUrl);
    };

    sourceElem.src = videoUrl;
    videoElem.src = videoUrl;
    videoElem.load();
    videoElem.play().catch(err => {
        console.error('Video play failed:', err, videoUrl);
    });
    
    // Load metrics
    document.getElementById('cam-direction').innerText = cam.metrics.dominant_direction;
    document.getElementById('cam-confidence').innerText = cam.metrics.confidence_score + "%";
    document.getElementById('cam-count').innerText = cam.metrics.total_movement_vectors;
    
    // Load distribution bars
    const dist = cam.metrics.directional_distribution;
    const total = Math.max(1, Object.values(dist).reduce((a,b)=>a+b, 0));
    
    ['North', 'South', 'East', 'West'].forEach(dir => {
        const val = dist[dir] || 0;
        const pct = (val / total) * 100;
        document.getElementById(`bar-${dir}`).style.width = pct + "%";
        document.getElementById(`val-${dir}`).innerText = val;
    });
    
    document.getElementById('video-panel').classList.remove('hidden');
}

function closePanel() {
    document.getElementById('video-panel').classList.add('hidden');
    document.getElementById('cam-video').pause();
}

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
    const scaleFactor = 0.0005; // Simulation multiplier 
    
    cameras.forEach(cam => {
        const latLng = cam.marker.getLatLng();
        const angleToCenter = Math.atan2(MAP_CENTER[0] - latLng.lat, MAP_CENTER[1] - latLng.lng);
        
        // We use the single mock dominant vector to generate 20 simulated trajectory points per camera
        for(let i=0; i<20; i++) {
            const noiseAngle = (Math.random() - 0.5) * 0.4;
            const finalAngle = angleToCenter + noiseAngle;
            
            // Speed noise
            const speed = 5.0 * (0.5 + Math.random());
            
            const projLat = latLng.lat + (Math.sin(finalAngle) * speed * scaleFactor);
            const projLng = latLng.lng + (Math.cos(finalAngle) * speed * scaleFactor);
            
            projectedPoints.push({ lat: projLat, lng: projLng, source: cam.id });
            
            if(Math.random() > 0.95) {
                L.polyline([[latLng.lat, latLng.lng], [projLat, projLng]], {
                    color: 'rgba(56, 189, 248, 0.2)', weight: 1
                }).addTo(trajectoriesLayer);
            }
        }
    });
    
    const clusters = dbscan(projectedPoints, 0.002, 10);
    let hotspotCount = 0;
    
    clusters.forEach(cluster => {
        if (cluster.length < 25) return; 
        hotspotCount++;
        
        let sumLat = 0; let sumLng = 0;
        cluster.forEach(p => { sumLat += p.lat; sumLng += p.lng; });
        const centerLat = sumLat / cluster.length;
        const centerLng = sumLng / cluster.length;
        
        const prob = Math.min(1.0, cluster.length / 150.0);
        const r = 255;
        const g = Math.floor(255 * (1 - prob));
        const color = `rgb(${r}, ${g}, 0)`;
        
        L.circle([centerLat, centerLng], {
            color: color, fillColor: color, fillOpacity: 0.6, radius: 60 + (prob * 100)
        }).addTo(hotspotsLayer);
    });
    
    document.getElementById('hotspot-count').innerText = hotspotCount;
}

window.recalculate = calculateConvergence;
window.onload = initMap;
