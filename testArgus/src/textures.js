import * as THREE from 'three';

// Procedural texture generators for photorealistic & sci-fi Earth rendering
export function createEarthTextures() {
  const width = 2048;
  const height = 1024;

  // 1. Daytime Surface Texture (Oceans, Continents, Mountains)
  const dayCanvas = document.createElement('canvas');
  dayCanvas.width = width;
  dayCanvas.height = height;
  const dayCtx = dayCanvas.getContext('2d');

  // Fill Ocean with deep blue gradient
  const oceanGrad = dayCtx.createLinearGradient(0, 0, 0, height);
  oceanGrad.addColorStop(0, '#061325');
  oceanGrad.addColorStop(0.5, '#0b2347');
  oceanGrad.addColorStop(1, '#051020');
  dayCtx.fillStyle = oceanGrad;
  dayCtx.fillRect(0, 0, width, height);

  // Draw Continents using simplified world polygon paths
  drawWorldLandmasses(dayCtx, width, height, '#1b3a2a', '#245238', '#406346');

  // 2. City Night Lights Texture
  const nightCanvas = document.createElement('canvas');
  nightCanvas.width = width;
  nightCanvas.height = height;
  const nightCtx = nightCanvas.getContext('2d');
  nightCtx.fillStyle = '#000000';
  nightCtx.fillRect(0, 0, width, height);

  drawCityClusters(nightCtx, width, height);

  // 3. Specular Map (White for ocean water, Black for land)
  const specCanvas = document.createElement('canvas');
  specCanvas.width = 1024;
  specCanvas.height = 512;
  const specCtx = specCanvas.getContext('2d');
  specCtx.fillStyle = '#ffffff';
  specCtx.fillRect(0, 0, 1024, 512);
  drawWorldLandmasses(specCtx, 1024, 512, '#000000', '#000000', '#000000');

  // 4. Cloud Cover Texture
  const cloudCanvas = document.createElement('canvas');
  cloudCanvas.width = 1024;
  cloudCanvas.height = 512;
  const cloudCtx = cloudCanvas.getContext('2d');
  drawCloudLayer(cloudCtx, 1024, 512);

  // Convert to Three.js Textures
  const dayTexture = new THREE.CanvasTexture(dayCanvas);
  dayTexture.colorSpace = THREE.SRGBColorSpace;
  dayTexture.wrapS = THREE.RepeatWrapping;
  dayTexture.wrapT = THREE.ClampToEdgeWrapping;

  const nightTexture = new THREE.CanvasTexture(nightCanvas);
  nightTexture.colorSpace = THREE.SRGBColorSpace;
  nightTexture.wrapS = THREE.RepeatWrapping;
  nightTexture.wrapT = THREE.ClampToEdgeWrapping;

  const specTexture = new THREE.CanvasTexture(specCanvas);
  specTexture.wrapS = THREE.RepeatWrapping;
  specTexture.wrapT = THREE.ClampToEdgeWrapping;

  const cloudTexture = new THREE.CanvasTexture(cloudCanvas);
  cloudTexture.wrapS = THREE.RepeatWrapping;
  cloudTexture.wrapT = THREE.ClampToEdgeWrapping;

  return {
    dayTexture,
    nightTexture,
    specTexture,
    cloudTexture
  };
}

// Draw world continents on equirectangular projection
function drawWorldLandmasses(ctx, w, h, landColor, highlandColor, mountainColor) {
  ctx.fillStyle = landColor;
  
  // Coordinates mapping function: (lon, lat) => (x, y)
  // lon: -180 to 180, lat: -90 to 90
  const toX = (lon) => ((lon + 180) / 360) * w;
  const toY = (lat) => ((90 - lat) / 180) * h;

  // Draw North America
  ctx.beginPath();
  ctx.moveTo(toX(-165), toY(65));
  ctx.bezierCurveTo(toX(-140), toY(72), toX(-100), toY(75), toX(-60), toY(60));
  ctx.bezierCurveTo(toX(-55), toY(45), toX(-75), toY(35), toX(-80), toY(25));
  ctx.bezierCurveTo(toX(-90), toY(18), toX(-100), toY(20), toX(-120), toY(35));
  ctx.bezierCurveTo(toX(-130), toY(50), toX(-155), toY(55), toX(-165), toY(65));
  ctx.fill();

  // Draw South America
  ctx.beginPath();
  ctx.moveTo(toX(-80), toY(10));
  ctx.bezierCurveTo(toX(-50), toY(5), toX(-35), toY(-5), toX(-40), toY(-25));
  ctx.bezierCurveTo(toX(-55), toY(-45), toX(-68), toY(-55), toX(-75), toY(-50));
  ctx.bezierCurveTo(toX(-75), toY(-30), toX(-80), toY(-10), toX(-80), toY(10));
  ctx.fill();

  // Draw Eurasia
  ctx.beginPath();
  ctx.moveTo(toX(-10), toY(35));
  ctx.bezierCurveTo(toX(0), toY(60), toX(30), toY(70), toX(90), toY(75));
  ctx.bezierCurveTo(toX(150), toY(75), toX(175), toY(65), toX(140), toY(40));
  ctx.bezierCurveTo(toX(120), toY(25), toX(105), toY(10), toX(80), toY(15));
  ctx.bezierCurveTo(toX(60), toY(25), toX(40), toY(30), toX(20), toY(35));
  ctx.bezierCurveTo(toX(5), toY(40), toX(-5), toY(45), toX(-10), toY(35));
  ctx.fill();

  // Draw Africa
  ctx.beginPath();
  ctx.moveTo(toX(-15), toY(30));
  ctx.bezierCurveTo(toX(10), toY(35), toX(35), toY(30), toX(50), toY(12));
  ctx.bezierCurveTo(toX(45), toY(-10), toX(35), toY(-30), toX(20), toY(-35));
  ctx.bezierCurveTo(toX(10), toY(-30), toX(0), toY(-10), toX(-15), toY(10));
  ctx.bezierCurveTo(toX(-20), toY(20), toX(-18), toY(28), toX(-15), toY(30));
  ctx.fill();

  // Draw Australia
  ctx.beginPath();
  ctx.moveTo(toX(115), toY(-20));
  ctx.bezierCurveTo(toX(135), toY(-12), toX(150), toY(-25), toX(145), toY(-38));
  ctx.bezierCurveTo(toX(130), toY(-38), toX(115), toY(-35), toX(115), toY(-20));
  ctx.fill();

  // Draw Greenland & Islands
  ctx.beginPath();
  ctx.moveTo(toX(-55), toY(80));
  ctx.bezierCurveTo(toX(-30), toY(82), toX(-20), toY(72), toX(-45), toY(62));
  ctx.fill();

  // Draw Japan & UK & Madagascar & SE Asia islands
  ctx.beginPath();
  ctx.arc(toX(140), toY(38), w * 0.015, 0, Math.PI * 2);
  ctx.arc(toX(-3), toY(54), w * 0.012, 0, Math.PI * 2);
  ctx.arc(toX(47), toY(-20), w * 0.01, 0, Math.PI * 2);
  ctx.arc(toX(100), toY(0), w * 0.016, 0, Math.PI * 2);
  ctx.arc(toX(112), toY(-5), w * 0.018, 0, Math.PI * 2);
  ctx.fill();

  // Add terrain accents (mountains & deserts)
  ctx.fillStyle = highlandColor;
  ctx.beginPath();
  // Rockies & Andes
  ctx.ellipse(toX(-110), toY(45), w * 0.018, h * 0.12, -0.3, 0, Math.PI * 2);
  ctx.ellipse(toX(-70), toY(-25), w * 0.012, h * 0.16, 0.15, 0, Math.PI * 2);
  // Himalayas & Alps
  ctx.ellipse(toX(85), toY(30), w * 0.04, h * 0.04, 0.2, 0, Math.PI * 2);
  ctx.ellipse(toX(12), toY(46), w * 0.015, h * 0.02, 0, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = mountainColor;
  // Sahara & Middle East desert accents
  ctx.beginPath();
  ctx.ellipse(toX(15), toY(22), w * 0.06, h * 0.05, 0, 0, Math.PI * 2);
  ctx.ellipse(toX(48), toY(24), w * 0.03, h * 0.04, 0, 0, Math.PI * 2);
  ctx.ellipse(toX(130), toY(-25), w * 0.03, h * 0.04, 0, 0, Math.PI * 2);
  ctx.fill();
}

// Draw glowing cyberpunk / city night clusters
function drawCityClusters(ctx, w, h) {
  const toX = (lon) => ((lon + 180) / 360) * w;
  const toY = (lat) => ((90 - lat) / 180) * h;

  // Major global hubs & population centers
  const hubs = [
    { lon: -74, lat: 40.7, size: 28, color: '#ffb347' }, // NYC
    { lon: -118, lat: 34, size: 24, color: '#ffa033' }, // LA
    { lon: -87.6, lat: 41.8, size: 20, color: '#ffc107' }, // Chicago
    { lon: -0.12, lat: 51.5, size: 26, color: '#00f0ff' }, // London
    { lon: 2.35, lat: 48.8, size: 24, color: '#ffcc00' }, // Paris
    { lon: 8.54, lat: 47.3, size: 20, color: '#00ffff' }, // Zurich
    { lon: 8.68, lat: 50.1, size: 22, color: '#66e0ff' }, // Frankfurt
    { lon: 37.6, lat: 55.7, size: 22, color: '#ffbb33' }, // Moscow
    { lon: 51.4, lat: 35.7, size: 22, color: '#ff9900' }, // Tehran
    { lon: 55.3, lat: 25.2, size: 20, color: '#00ffcc' }, // Dubai
    { lon: 77.2, lat: 28.6, size: 25, color: '#ff9933' }, // Delhi
    { lon: 72.8, lat: 19.0, size: 24, color: '#ffaa44' }, // Mumbai
    { lon: 103.8, lat: 1.35, size: 22, color: '#00f3ff' }, // Singapore
    { lon: 116.4, lat: 39.9, size: 26, color: '#ff9933' }, // Beijing
    { lon: 121.5, lat: 31.2, size: 28, color: '#ffaa00' }, // Shanghai
    { lon: 139.7, lat: 35.6, size: 30, color: '#00e5ff' }, // Tokyo
    { lon: 126.9, lat: 37.5, size: 24, color: '#66ffff' }, // Seoul
    { lon: 151.2, lat: -33.8, size: 20, color: '#ffb84d' }, // Sydney
    { lon: -46.6, lat: -23.5, size: 24, color: '#ff9933' }, // São Paulo
  ];

  hubs.forEach(hub => {
    const x = toX(hub.lon);
    const y = toY(hub.lat);
    
    // Core intense burst
    const grad = ctx.createRadialGradient(x, y, 0, x, y, hub.size);
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.2, hub.color);
    grad.addColorStop(0.6, 'rgba(255, 170, 0, 0.4)');
    grad.addColorStop(1, 'rgba(255, 150, 0, 0)');

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(x, y, hub.size, 0, Math.PI * 2);
    ctx.fill();

    // Sprawling micro speckles around city hub
    for (let i = 0; i < 35; i++) {
      const angle = Math.random() * Math.PI * 2;
      const dist = Math.random() * (hub.size * 1.8);
      const px = x + Math.cos(angle) * dist;
      const py = y + Math.sin(angle) * dist;
      ctx.fillStyle = Math.random() > 0.3 ? 'rgba(255, 210, 100, 0.8)' : 'rgba(0, 240, 255, 0.7)';
      ctx.fillRect(px, py, 1.5, 1.5);
    }
  });

  // Random galactic grid data traces
  ctx.strokeStyle = 'rgba(0, 230, 255, 0.15)';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 8]);
  for (let i = 0; i < 6; i++) {
    const start = hubs[Math.floor(Math.random() * hubs.length)];
    const end = hubs[Math.floor(Math.random() * hubs.length)];
    ctx.beginPath();
    ctx.moveTo(toX(start.lon), toY(start.lat));
    ctx.quadraticCurveTo(
      (toX(start.lon) + toX(end.lon)) / 2,
      Math.min(toY(start.lat), toY(end.lat)) - 40,
      toX(end.lon),
      toY(end.lat)
    );
    ctx.stroke();
  }
}

// Procedural swirling clouds
function drawCloudLayer(ctx, w, h) {
  ctx.fillStyle = 'rgba(0, 0, 0, 0)';
  ctx.clearRect(0, 0, w, h);

  // Generate atmospheric weather bands
  for (let y = 0; y < h; y += 4) {
    const lat = (h / 2 - y) / (h / 2); // -1 to 1
    const density = Math.cos(lat * Math.PI * 1.5) * 0.4 + 0.3;

    for (let x = 0; x < w; x += 6) {
      const noise = (Math.sin(x * 0.02 + y * 0.03) + Math.cos(x * 0.05 - y * 0.01) + 2) / 4;
      if (noise * density > 0.45) {
        const alpha = Math.min(0.85, (noise * density - 0.45) * 2.2);
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha.toFixed(2)})`;
        ctx.fillRect(x, y, 6, 4);
      }
    }
  }

  // Draw tropical cyclone vortexes
  drawCyclone(ctx, w * 0.25, h * 0.35, 45);
  drawCyclone(ctx, w * 0.72, h * 0.32, 55);
  drawCyclone(ctx, w * 0.45, h * 0.65, 40);
}

function drawCyclone(ctx, cx, cy, r) {
  ctx.save();
  ctx.translate(cx, cy);
  for (let i = 0; i < 8; i++) {
    ctx.rotate(0.4);
    const grad = ctx.createRadialGradient(0, 0, 2, 0, 0, r);
    grad.addColorStop(0, 'rgba(255, 255, 255, 0.85)');
    grad.addColorStop(0.5, 'rgba(230, 245, 255, 0.4)');
    grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.ellipse(r * 0.3, 0, r * 0.6, r * 0.25, 0.5, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}
