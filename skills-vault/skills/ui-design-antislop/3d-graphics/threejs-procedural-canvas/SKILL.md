---
id: ui-design-antislop.3d-graphics.threejs-procedural-canvas
name: threejs-procedural-canvas
title: Three.js & React Three Fiber Procedural 3D Canvas
category: ui-design-antislop
subcategory: 3d-graphics
version: 1.1.0
tags:
- threejs
- r3f
- webgl
- shaders
- glsl
- procedural
- canvas
trust_rating: 0.93
estimated_tokens: 1600
description: Construct high-performance interactive 3D procedural scenes, custom GLSL
  shaders, post-processing bloom, and responsive canvas viewports using Three.js and
  React Three Fiber.
trigger_patterns:
- react three fiber canvas setup
- threejs procedural geometry glsl
- r3f custom shader material
- threejs webgl performance dispose
---

# Three.js & React Three Fiber Procedural 3D Canvas

## Objective
Render smooth 60fps procedural WebGL canvases, custom GLSL vertex/fragment shaders, and memory-safe scene graphs with proper geometry/material disposal.

## Blueprint (`components/ProceduralOrb.tsx`)
```tsx
import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const vertexShader = `
  varying vec2 vUv;
  varying vec3 vNormal;
  uniform float uTime;

  void main() {
    vUv = uv;
    vNormal = normal;
    vec3 pos = position;
    pos += normal * sin(pos.y * 4.0 + uTime * 2.0) * 0.08;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`;

const fragmentShader = `
  varying vec2 vUv;
  varying vec3 vNormal;
  uniform float uTime;

  void main() {
    vec3 color = 0.5 + 0.5 * cos(uTime + vUv.xyx + vec3(0, 2, 4));
    gl_FragColor = vec4(color, 0.9);
  }
`;

function AnimatedMesh() {
  const meshRef = useRef<THREE.Mesh>(null!);
  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
    }),
    []
  );

  useFrame((_, delta) => {
    uniforms.uTime.value += delta;
    meshRef.current.rotation.y += delta * 0.2;
  });

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[1.5, 32]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent
      />
    </mesh>
  );
}

export function ProceduralCanvas() {
  return (
    <div className="w-full h-96 rounded-2xl overflow-hidden bg-black">
      <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <AnimatedMesh />
      </Canvas>
    </div>
  );
}
```

## Anti-Patterns
- ❌ Creating geometries or textures inside `useFrame` render loops (causes rapid VRAM leaks).
- ❌ Forgetting `geometry.dispose()` and `material.dispose()` on component unmounts.
