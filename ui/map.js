let map;
let cameras = [];
let hotspotsLayer;
let trajectoriesLayer;
let analyticsDB = [];
let activeCameraIndex = -1;

const MAP_CENTER = [40.7580, -73.9855]; 

function initMap() {
    map = L.map('map', { zoomControl: false }).setView(MAP_CENTER, 15);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CARTO'
    }).addTo(map);

    hotspotsLayer = L.layerGroup().addTo(map);
    trajectoriesLayer = L.layerGroup().addTo(map);

    fetchData();
    setupVideoSync();
}

async function fetchData() {
    try {
        const response = await fetch('camera_analytics.json');
        analyticsDB = await response.json();
        setupCameras();
    } catch (e) {
        console.warn("Could not load camera_analytics.json", e);
    }
}

function setupCameras() {
    analyticsDB.forEach((camData, i) => {
        // Fixed cameras, dragging disabled as they are real existing coordinates
        const marker = L.marker([camData.lat, camData.lng], { draggable: false }).addTo(map);
        marker.on('click', () => openPanel(i));
        
        cameras.push({
            id: camData.id,
            marker: marker,
            data: camData
        });
    });
    calculateConvergence();
}

function setupVideoSync() {
    const videoElem = document.getElementById('cam-video');
    videoElem.addEventListener('timeupdate', () => {
        if (activeCameraIndex === -1) return;
        const camData = cameras[activeCameraIndex].data;
        if (!camData.time_series || camData.time_series.length === 0) return;
        
        const currTime = videoElem.currentTime;
        let closestFrame = camData.time_series[0];
        let minDiff = Infinity;
        
        for (let i=0; i<camData.time_series.length; i++) {
            const diff = Math.abs(camData.time_series[i].time - currTime);
            if (diff < minDiff) {
                minDiff = diff;
                closestFrame = camData.time_series[i];
            }
        }
        
        updateSidebarStats(closestFrame);
    });
}

function updateSidebarStats(frameData) {
    document.getElementById('cam-count').innerText = frameData.total;
    
    let dominantDir = "N/A";
    let maxVal = -1;
    let totalVals = 0;
    
    ['North', 'South', 'East', 'West'].forEach(dir => {
        const val = frameData.counts[dir] || 0;
        totalVals += val;
        if (val > maxVal) {
            maxVal = val;
            dominantDir = dir;
        }
        
        const pct = frameData.total > 0 ? (val / frameData.total) * 100 : 0;
        document.getElementById(`bar-${dir}`).style.width = pct + "%";
        document.getElementById(`val-${dir}`).innerText = val;
    });
    
    document.getElementById('cam-direction').innerText = dominantDir;
    const confidence = totalVals > 0 ? (maxVal / totalVals) * 100 : 0;
    document.getElementById('cam-confidence').innerText = confidence.toFixed(1) + "%";
}

function openPanel(index) {
    activeCameraIndex = index;
    const cam = cameras[index].data;
    document.getElementById('cam-title').innerText = cam.id + " Analytics";
    
    const videoElem = document.getElementById('cam-video');
    videoElem.src = cam.video_path;
    videoElem.load();
    videoElem.play();
    
    document.getElementById('video-panel').classList.remove('hidden');
}

function closePanel() {
    activeCameraIndex = -1;
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
    
    cameras.forEach(camWrap => {
        const cam = camWrap.data;
        const latLng = camWrap.marker.getLatLng();
        
        // Rigid calibration mapping based on real-world camera geometry
        const headingRad = (cam.heading * Math.PI) / 180;
        const scaleFactor = cam.scale_pixels_to_meters * 0.00005;
        
        if (cam.time_series && cam.time_series.length > 0) {
            let sumDx = 0; let sumDy = 0;
            let count = 0;
            for(let j=0; j<Math.min(50, cam.time_series.length); j++) {
                sumDx += cam.time_series[j].dominant_vector_dx;
                sumDy += cam.time_series[j].dominant_vector_dy;
                count++;
            }
            if(count > 0) {
                sumDx /= count; sumDy /= count;
            }
            
            // Map (dx,dy) to Geographic (Lat/Lng) based on fixed real-world heading
            for(let i=0; i<15; i++) {
                const noise = (Math.random() - 0.5) * 5;
                const vx = sumDx + noise;
                const vy = sumDy + noise;
                
                const geoLatOffset = (vy * Math.cos(headingRad) - vx * Math.sin(headingRad)) * scaleFactor;
                const geoLngOffset = (vx * Math.cos(headingRad) + vy * Math.sin(headingRad)) * scaleFactor;
                
                const projLat = latLng.lat + geoLatOffset * 50; 
                const projLng = latLng.lng + geoLngOffset * 50;
                
                projectedPoints.push({ lat: projLat, lng: projLng, source: cam.id });
                
                if(Math.random() > 0.8) {
                    L.polyline([[latLng.lat, latLng.lng], [projLat, projLng]], {
                        color: 'rgba(56, 189, 248, 0.2)', weight: 1
                    }).addTo(trajectoriesLayer);
                }
            }
        }
    });
    
    const clusters = dbscan(projectedPoints, 0.002, 10);
    let hotspotCount = 0;
    
    clusters.forEach(cluster => {
        if (cluster.length < 15) return; 
        hotspotCount++;
        
        let sumLat = 0; let sumLng = 0;
        cluster.forEach(p => { sumLat += p.lat; sumLng += p.lng; });
        const centerLat = sumLat / cluster.length;
        const centerLng = sumLng / cluster.length;
        
        const prob = Math.min(1.0, cluster.length / 100.0);
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
