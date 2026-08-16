import * as THREE from 'three';

// Custom Atmosphere Rayleigh Fresnel Shader
export const AtmosphereShader = {
  uniforms: {
    color: { value: new THREE.Color(0x38bdf8) }, // Cyan atmosphere
    glowPower: { value: 3.8 },
    viewVector: { value: new THREE.Vector3() }
  },
  vertexShader: `
    uniform vec3 viewVector;
    uniform float glowPower;
    varying float intensity;
    varying vec3 vNormal;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      vec3 viewDir = normalize(-mvPosition.xyz);
      // Fresnel calculation
      intensity = pow(1.0 - max(0.0, dot(vNormal, viewDir)), glowPower);
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  fragmentShader: `
    uniform vec3 color;
    varying float intensity;
    void main() {
      vec3 glow = color * intensity * 1.6;
      gl_FragColor = vec4(glow, intensity * 0.95);
    }
  `
};

// Custom Pulsing Energy Ring Shader
export const OrbitRingShader = {
  uniforms: {
    color: { value: new THREE.Color(0x00f0ff) },
    time: { value: 0.0 },
    radius: { value: 1.0 },
    thickness: { value: 0.04 },
    opacity: { value: 0.8 }
  },
  vertexShader: `
    varying vec2 vUv;
    varying vec3 vPosition;
    void main() {
      vUv = uv;
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 color;
    uniform float time;
    uniform float opacity;
    varying vec2 vUv;
    varying vec3 vPosition;
    void main() {
      // Create dashing particle pulses traveling around the ring
      float angle = atan(vPosition.y, vPosition.x);
      float pulse = sin(angle * 6.0 - time * 3.0) * 0.5 + 0.5;
      float pulse2 = sin(angle * 12.0 + time * 2.0) * 0.5 + 0.5;
      
      float alpha = (0.35 + pulse * 0.55 + pulse2 * 0.2) * opacity;
      gl_FragColor = vec4(color + vec3(pulse * 0.4), alpha);
    }
  `
};
