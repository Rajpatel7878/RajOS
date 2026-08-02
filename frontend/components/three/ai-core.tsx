'use client';

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Float, Icosahedron, MeshDistortMaterial, Torus } from '@react-three/drei';
import * as THREE from 'three';

function ParticleField({ count = 2000 }: { count?: number }) {
  const ref = useRef<THREE.Points>(null);

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const radius = 4 + Math.random() * 6;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = radius * Math.cos(phi);
    }
    return arr;
  }, [count]);

  useFrame((state) => {
    if (!ref.current) return;
    const t = state.clock.elapsedTime;
    ref.current.rotation.y = t * 0.05;
    ref.current.rotation.x = Math.sin(t * 0.1) * 0.1;
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#38bdf8"
        size={0.025}
        sizeAttenuation
        depthWrite={false}
        opacity={0.7}
      />
    </Points>
  );
}

function CoreOrb() {
  const meshRef = useRef<THREE.Mesh>(null);
  const torusRef = useRef<THREE.Mesh>(null);
  const torus2Ref = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (meshRef.current) {
      meshRef.current.rotation.y = t * 0.2;
      meshRef.current.rotation.x = t * 0.1;
    }
    if (torusRef.current) {
      torusRef.current.rotation.x = t * 0.5;
      torusRef.current.rotation.y = t * 0.3;
    }
    if (torus2Ref.current) {
      torus2Ref.current.rotation.y = t * -0.4;
      torus2Ref.current.rotation.z = t * 0.2;
    }
  });

  return (
    <group>
      <Float speed={1.5} rotationIntensity={0.4} floatIntensity={0.6}>
        <Icosahedron ref={meshRef} args={[1.6, 4]}>
          <MeshDistortMaterial
            color="#0ea5e9"
            emissive="#0284c7"
            emissiveIntensity={0.4}
            roughness={0.1}
            metalness={0.9}
            distort={0.35}
            speed={2}
          />
        </Icosahedron>
      </Float>
      <Torus ref={torusRef} args={[2.6, 0.015, 16, 100]}>
        <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={1.5} transparent opacity={0.6} />
      </Torus>
      <Torus ref={torus2Ref} args={[3.1, 0.012, 16, 100]} rotation={[Math.PI / 3, 0, 0]}>
        <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={1.2} transparent opacity={0.4} />
      </Torus>
    </group>
  );
}

export function AICore({ className }: { className?: string }) {
  return (
    <div className={className}>
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }} dpr={[1, 2]}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1.2} color="#38bdf8" />
        <pointLight position={[-10, -5, -10]} intensity={0.8} color="#22d3ee" />
        <CoreOrb />
        <ParticleField count={1500} />
      </Canvas>
    </div>
  );
}
