import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { createEarthTextures } from './textures.js';
import { AtmosphereShader } from './shaders.js';
import { ORBITAL_PLANS, GROUND_STATIONS } from './plans.js';
import { sounds } from './audio.js';

export class OrbitScene {
  constructor(canvasContainer, callbacks = {}) {
    this.container = canvasContainer;
    this.onOrbitSelect = callbacks.onOrbitSelect || (() => {});
    this.onHoverChange = callbacks.onHoverChange || (() => {});
    this.onTelemetryUpdate = callbacks.onTelemetryUpdate || (() => {});

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;

    this.earthGroup = null;
    this.earthMesh = null;
    this.cloudMesh = null;
    this.atmosphereMesh = null;

    this.orbitGroups = [];
    this.satellites = [];
    this.groundStationMeshes = [];
    this.laserBeams = [];

    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2(-100, -100);
    this.hoveredObject = null;
    this.selectedOrbitTier = null;

    this.isAutoRotate = true;
    this.showLaserBeams = true;
    this.clock = new THREE.Clock();

    // Camera animation target
    this.cameraTargetPos = new THREE.Vector3(0, 4, 11);
    this.controlsTargetPos = new THREE.Vector3(0, 0, 0);
    this.isTransitioningCamera = false;

    this.init();
  }

  init() {
    // 1. Scene & Renderer Setup
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x020712, 0.015);

    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;

    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    this.camera.position.set(0, 3.5, 11);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;
    this.container.appendChild(this.renderer.domElement);

    // 2. Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.minDistance = 3.8;
    this.controls.maxDistance = 24;
    this.controls.enablePan = false;
    this.controls.maxPolarAngle = Math.PI * 0.92;
    this.controls.minPolarAngle = Math.PI * 0.08;

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0x1a2e4a, 1.4);
    this.scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 2.8);
    sunLight.position.set(15, 6, 12);
    this.scene.add(sunLight);

    const rimLight = new THREE.DirectionalLight(0x00f0ff, 1.2);
    rimLight.position.set(-15, -4, -10);
    this.scene.add(rimLight);

    // 4. Build Environment & Objects
    this.buildStarfield();
    this.buildEarth();
    this.buildGroundStations();
    this.buildOrbitalConstellations();

    // 5. Event Listeners
    window.addEventListener('resize', this.onResize.bind(this));
    this.renderer.domElement.addEventListener('mousemove', this.onMouseMove.bind(this));
    this.renderer.domElement.addEventListener('click', this.onClick.bind(this));
    this.renderer.domElement.addEventListener('touchstart', this.onTouchStart.bind(this), { passive: true });

    // Start render loop
    this.animate();
  }

  buildStarfield() {
    const starCount = 3500;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);

    const colorPalette = [
      new THREE.Color(0xffffff),
      new THREE.Color(0x88ccff),
      new THREE.Color(0xaaccff),
      new THREE.Color(0xffeebb),
      new THREE.Color(0x00f0ff)
    ];

    for (let i = 0; i < starCount; i++) {
      const radius = 120 + Math.random() * 200;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);

      const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 1.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.85
    });

    const starfield = new THREE.Points(geometry, material);
    this.scene.add(starfield);
  }

  buildEarth() {
    this.earthGroup = new THREE.Group();
    this.earthRadius = 2.4;

    const { dayTexture, nightTexture, specTexture, cloudTexture } = createEarthTextures();

    // 1. Base Earth Mesh
    const earthGeo = new THREE.SphereGeometry(this.earthRadius, 64, 64);
    const earthMat = new THREE.MeshStandardMaterial({
      map: dayTexture,
      roughness: 0.55,
      metalness: 0.1,
      roughnessMap: specTexture
    });

    // Blend night lights
    earthMat.onBeforeCompile = (shader) => {
      shader.uniforms.nightTexture = { value: nightTexture };
      shader.fragmentShader = `
        uniform sampler2D nightTexture;
      ` + shader.fragmentShader;

      shader.fragmentShader = shader.fragmentShader.replace(
        '#include <map_fragment>',
        `
        #include <map_fragment>
        vec4 nightColor = texture2D(nightTexture, vMapUv);
        // Compute diffuse daylight intensity
        vec3 lightDir = normalize(vec3(15.0, 6.0, 12.0));
        float dayDot = dot(normalize(vNormal), lightDir);
        float nightFactor = smoothstep(0.15, -0.25, dayDot);
        diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb + nightColor.rgb * 1.8, nightFactor);
        `
      );
    };

    this.earthMesh = new THREE.Mesh(earthGeo, earthMat);
    this.earthGroup.add(this.earthMesh);

    // 2. Swirling Cloud Layer
    const cloudGeo = new THREE.SphereGeometry(this.earthRadius + 0.035, 64, 64);
    const cloudMat = new THREE.MeshStandardMaterial({
      map: cloudTexture,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    this.cloudMesh = new THREE.Mesh(cloudGeo, cloudMat);
    this.earthGroup.add(this.cloudMesh);

    // 3. Glowing Atmospheric Rim Layer
    const atmosGeo = new THREE.SphereGeometry(this.earthRadius + 0.22, 64, 64);
    const atmosMat = new THREE.ShaderMaterial({
      vertexShader: AtmosphereShader.vertexShader,
      fragmentShader: AtmosphereShader.fragmentShader,
      uniforms: AtmosphereShader.uniforms,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
      transparent: true,
      depthWrite: false
    });
    this.atmosphereMesh = new THREE.Mesh(atmosGeo, atmosMat);
    this.earthGroup.add(this.atmosphereMesh);

    this.scene.add(this.earthGroup);
  }

  buildGroundStations() {
    const toVec3 = (lon, lat, r) => {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lon + 180) * (Math.PI / 180);
      return new THREE.Vector3(
        -(r * Math.sin(phi) * Math.cos(theta)),
        r * Math.cos(phi),
        r * Math.sin(phi) * Math.sin(theta)
      );
    };

    GROUND_STATIONS.forEach((station) => {
      const pos = toVec3(station.lon, station.lat, this.earthRadius + 0.01);

      // Station Hub Ring
      const ringGeo = new THREE.RingGeometry(0.04, 0.07, 24);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x00f0ff,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.9
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.position.copy(pos);
      ring.lookAt(new THREE.Vector3(0, 0, 0));
      this.earthGroup.add(ring);

      // Station Pillar Dot
      const dotGeo = new THREE.SphereGeometry(0.035, 12, 12);
      const dotMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const dot = new THREE.Mesh(dotGeo, dotMat);
      dot.position.copy(pos);
      this.earthGroup.add(dot);

      this.groundStationMeshes.push({ mesh: dot, pos, data: station });
    });
  }

  buildOrbitalConstellations() {
    const orbitConfigs = [
      { tier: 1, radius: 3.3, inclination: 0.45, rotSpeed: 0.28, count: 6, color: 0x00f0ff, plan: ORBITAL_PLANS[0] },
      { tier: 2, radius: 4.5, inclination: -0.62, rotSpeed: 0.19, count: 5, color: 0xa855f7, plan: ORBITAL_PLANS[1] },
      { tier: 3, radius: 6.2, inclination: 0.05, rotSpeed: 0.09, count: 4, color: 0xf59e0b, plan: ORBITAL_PLANS[2] },
      { tier: 4, radius: 3.9, inclination: 1.45, rotSpeed: 0.22, count: 4, color: 0x10b981, plan: ORBITAL_PLANS[3] }
    ];

    orbitConfigs.forEach((cfg) => {
      const orbitGroup = new THREE.Group();
      orbitGroup.rotation.x = cfg.inclination;
      orbitGroup.rotation.z = cfg.inclination * 0.4;
      orbitGroup.userData = { cfg, plan: cfg.plan };

      // 1. Glowing Orbital Ring Path
      const ringRadius = cfg.radius;
      const tubeRadius = 0.018;
      const ringGeo = new THREE.TorusGeometry(ringRadius, tubeRadius, 16, 120);
      const ringMat = new THREE.MeshBasicMaterial({
        color: cfg.color,
        transparent: true,
        opacity: 0.55,
        wireframe: false
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2;
      ringMesh.userData = { isOrbitRing: true, plan: cfg.plan, tier: cfg.tier };
      orbitGroup.add(ringMesh);

      // Invisible larger hit-area for easy clicking & hovering
      const hitGeo = new THREE.TorusGeometry(ringRadius, 0.22, 8, 48);
      const hitMat = new THREE.MeshBasicMaterial({ visible: false });
      const hitMesh = new THREE.Mesh(hitGeo, hitMat);
      hitMesh.rotation.x = Math.PI / 2;
      hitMesh.userData = { isOrbitRing: true, plan: cfg.plan, tier: cfg.tier, targetRing: ringMesh };
      orbitGroup.add(hitMesh);

      // 2. Spawn Satellites along this orbit
      for (let i = 0; i < cfg.count; i++) {
        const angle = (i / cfg.count) * Math.PI * 2;
        const satMesh = this.createSatelliteMesh(cfg.color, cfg.plan);
        satMesh.position.set(
          Math.cos(angle) * ringRadius,
          0,
          Math.sin(angle) * ringRadius
        );
        satMesh.userData = {
          orbitRadius: ringRadius,
          angle,
          speed: cfg.rotSpeed,
          plan: cfg.plan,
          tier: cfg.tier,
          id: `${cfg.plan.code}-SAT-${i + 1}`
        };
        orbitGroup.add(satMesh);
        this.satellites.push(satMesh);
      }

      this.scene.add(orbitGroup);
      this.orbitGroups.push({ group: orbitGroup, ringMesh, cfg });
    });
  }

  createSatelliteMesh(primaryColor, plan) {
    const satGroup = new THREE.Group();

    // Central Chassis (Gold foil / Carbon)
    const bodyGeo = new THREE.BoxGeometry(0.12, 0.08, 0.12);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0xd4af37,
      metalness: 0.9,
      roughness: 0.2
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    satGroup.add(body);

    // Solar Panel Wings (Left & Right)
    const wingGeo = new THREE.BoxGeometry(0.32, 0.015, 0.1);
    const wingMat = new THREE.MeshStandardMaterial({
      color: 0x1e3a8a,
      metalness: 0.6,
      roughness: 0.3,
      emissive: 0x0a2550,
      emissiveIntensity: 0.3
    });

    const leftWing = new THREE.Mesh(wingGeo, wingMat);
    leftWing.position.x = -0.25;
    satGroup.add(leftWing);

    const rightWing = new THREE.Mesh(wingGeo, wingMat);
    rightWing.position.x = 0.25;
    satGroup.add(rightWing);

    // Telemetry Pulsing Beacon Light
    const beaconGeo = new THREE.SphereGeometry(0.04, 8, 8);
    const beaconMat = new THREE.MeshBasicMaterial({
      color: primaryColor,
      transparent: true,
      opacity: 0.95
    });
    const beacon = new THREE.Mesh(beaconGeo, beaconMat);
    beacon.position.y = 0.06;
    satGroup.add(beacon);

    // Holographic Reticle Ring
    const reticleGeo = new THREE.RingGeometry(0.18, 0.21, 16);
    const reticleMat = new THREE.MeshBasicMaterial({
      color: primaryColor,
      transparent: true,
      opacity: 0.6,
      side: THREE.DoubleSide
    });
    const reticle = new THREE.Mesh(reticleGeo, reticleMat);
    reticle.rotation.x = Math.PI / 2;
    reticle.userData = { isReticle: true };
    satGroup.add(reticle);

    satGroup.userData = { isSatellite: true, plan, beacon, reticle };
    return satGroup;
  }

  // Smooth camera animation towards selected orbit
  focusOrbit(tier) {
    this.selectedOrbitTier = tier;
    const targetGroup = this.orbitGroups.find(o => o.cfg.tier === tier);
    if (!targetGroup) return;

    sounds.playOrbitSelect();

    const radius = targetGroup.cfg.radius;
    const inc = targetGroup.cfg.inclination;

    // Calculate camera vantage point
    const camDist = radius + 2.8;
    this.cameraTargetPos = new THREE.Vector3(
      Math.cos(inc) * camDist * 0.8,
      Math.sin(inc) * camDist + 1.2,
      Math.sin(inc * 0.5) * camDist + 3.2
    );
    this.controlsTargetPos = new THREE.Vector3(0, 0, 0);
    this.isTransitioningCamera = true;

    // Highlight selected ring
    this.orbitGroups.forEach(og => {
      if (og.cfg.tier === tier) {
        og.ringMesh.material.opacity = 1.0;
        og.ringMesh.scale.set(1.02, 1.02, 1.02);
      } else {
        og.ringMesh.material.opacity = 0.25;
        og.ringMesh.scale.set(1.0, 1.0, 1.0);
      }
    });

    this.onOrbitSelect(targetGroup.cfg.plan);
  }

  resetCamera() {
    this.cameraTargetPos = new THREE.Vector3(0, 3.5, 11);
    this.controlsTargetPos = new THREE.Vector3(0, 0, 0);
    this.isTransitioningCamera = true;
    this.selectedOrbitTier = null;

    this.orbitGroups.forEach(og => {
      og.ringMesh.material.opacity = 0.55;
      og.ringMesh.scale.set(1.0, 1.0, 1.0);
    });
  }

  onMouseMove(e) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    this.checkHover(e.clientX, e.clientY);
  }

  onTouchStart(e) {
    if (e.touches.length > 0) {
      const touch = e.touches[0];
      const rect = this.renderer.domElement.getBoundingClientRect();
      this.mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
      this.checkHover(touch.clientX, touch.clientY);
    }
  }

  checkHover(screenX, screenY) {
    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.scene.children, true);

    let foundTarget = null;

    for (let hit of intersects) {
      const obj = hit.object;
      if (obj.userData && (obj.userData.isOrbitRing || obj.userData.isSatellite)) {
        foundTarget = obj;
        break;
      }
      if (obj.parent && obj.parent.userData && obj.parent.userData.isSatellite) {
        foundTarget = obj.parent;
        break;
      }
    }

    if (foundTarget) {
      this.renderer.domElement.style.cursor = 'pointer';
      const plan = foundTarget.userData.plan;
      if (this.hoveredObject !== foundTarget) {
        this.hoveredObject = foundTarget;
        sounds.playHover();
        this.onHoverChange({
          isHovered: true,
          plan,
          screenX,
          screenY,
          tier: foundTarget.userData.tier
        });
      }
    } else {
      this.renderer.domElement.style.cursor = 'grab';
      if (this.hoveredObject) {
        this.hoveredObject = null;
        this.onHoverChange({ isHovered: false });
      }
    }
  }

  onClick(e) {
    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.scene.children, true);

    for (let hit of intersects) {
      const obj = hit.object;
      if (obj.userData && obj.userData.isOrbitRing) {
        this.focusOrbit(obj.userData.tier);
        return;
      }
      if (obj.userData && obj.userData.isSatellite) {
        this.focusOrbit(obj.userData.tier);
        return;
      }
      if (obj.parent && obj.parent.userData && obj.parent.userData.isSatellite) {
        this.focusOrbit(obj.parent.userData.tier);
        return;
      }
    }
  }

  onResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  animate() {
    requestAnimationFrame(this.animate.bind(this));

    const delta = this.clock.getDelta();
    const elapsedTime = this.clock.getElapsedTime();

    // 1. Earth Rotation
    if (this.earthGroup) {
      this.earthMesh.rotation.y += 0.04 * delta;
      this.cloudMesh.rotation.y += 0.055 * delta;
    }

    // 2. Orbital Constellations & Satellites Kinematics
    this.orbitGroups.forEach((og) => {
      if (this.isAutoRotate) {
        og.group.rotation.y += og.cfg.rotSpeed * 0.15 * delta;
      }
    });

    // Satellites local animations
    this.satellites.forEach((sat) => {
      // Pulse beacon light
      if (sat.userData.beacon) {
        const pulse = 0.5 + 0.5 * Math.sin(elapsedTime * 4.5 + sat.position.x);
        sat.userData.beacon.material.opacity = pulse;
      }
      // Reticle spin
      if (sat.userData.reticle) {
        sat.userData.reticle.rotation.z += 1.5 * delta;
      }
    });

    // 3. Smooth Camera Transitions
    if (this.isTransitioningCamera) {
      this.camera.position.lerp(this.cameraTargetPos, 0.045);
      this.controls.target.lerp(this.controlsTargetPos, 0.045);

      if (this.camera.position.distanceTo(this.cameraTargetPos) < 0.08) {
        this.isTransitioningCamera = false;
      }
    }

    // 4. Update Orbit Controls
    this.controls.update();

    // 5. Render Scene
    this.renderer.render(this.scene, this.camera);
  }
}
