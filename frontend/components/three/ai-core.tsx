'use client';

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import {
  Points,
  PointMaterial,
  Float,
  Icosahedron,
  MeshDistortMaterial,
  Torus,
  Environment,
  Sphere,
} from '@react-three/drei';
import * as THREE from 'three';

/* ── Dual-colour particle field (sky-blue + violet) ──────────────────── */
function ParticleField({ count = 3000 }: { count?: number }) {
  const skyRef = useRef<THREE.Points>(null);
  const violetRef = useRef<THREE.Points>(null);

  const half = Math.floor(count / 2);

  const skyPositions = useMemo(() => {
    const arr = new Float32Array(half * 3);
    for (let i = 0; i < half; i++) {
      const radius = 4 + Math.random() * 6;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3]     = radius * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = radius * Math.cos(phi);
    }
    return arr;
  }, [half]);

  const violetPositions = useMemo(() => {
    const arr = new Float32Array((count - half) * 3);
    for (let i = 0; i < count - half; i++) {
      const radius = 5 + Math.random() * 7;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3]     = radius * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = radius * Math.cos(phi);
    }
    return arr;
  }, [count, half]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (skyRef.current) {
      skyRef.current.rotation.y = t * 0.05;
      skyRef.current.rotation.x = Math.sin(t * 0.1) * 0.1;
    }
    if (violetRef.current) {
      violetRef.current.rotation.y = -t * 0.04;
      violetRef.current.rotation.z = Math.sin(t * 0.08) * 0.08;
    }
  });

  return (
    <>
      <Points ref={skyRef} positions={skyPositions} stride={3} frustumCulled={false}>
        <PointMaterial transparent color="#38bdf8" size={0.022} sizeAttenuation depthWrite={false} opacity={0.75} />
      </Points>
      <Points ref={violetRef} positions={violetPositions} stride={3} frustumCulled={false}>
        <PointMaterial transparent color="#a78bfa" size={0.018} sizeAttenuation depthWrite={false} opacity={0.5} />
      </Points>
    </>
  );
}

/* ── Orbiting satellites ─────────────────────────────────────────────── */
function Satellite({
  radius,
  speed,
  size,
  color,
  tilt = 0,
}: {
  radius: number;
  speed: number;
  size: number;
  color: string;
  tilt?: number;
}) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime * speed;
    if (ref.current) {
      ref.current.position.x = Math.cos(t) * radius;
      ref.current.position.y = Math.sin(t) * radius * Math.sin(tilt);
      ref.current.position.z = Math.sin(t) * radius * Math.cos(tilt);
    }
  });

  return (
    <Sphere ref={ref} args={[size, 16, 16]}>
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={1.8}
        roughness={0.2}
        metalness={0.8}
      />
    </Sphere>
  );
}

/* ── Holographic ring-grid disc ──────────────────────────────────────── */
function HoloDisc() {
  const ringRefs = useRef<(THREE.Mesh | null)[]>([]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    ringRefs.current.forEach((r, i) => {
      if (r) r.rotation.z = t * (i % 2 === 0 ? 0.08 : -0.06) + i;
    });
  });

  const rings = [2.2, 2.7, 3.15, 3.55];

  return (
    <group rotation={[Math.PI / 2.3, 0, 0]}>
      {rings.map((r, i) => (
        <mesh
          key={r}
          ref={(el) => { ringRefs.current[i] = el; }}
        >
          <torusGeometry args={[r, 0.01, 8, 80]} />
          <meshStandardMaterial
            color={i % 2 === 0 ? '#22d3ee' : '#818cf8'}
            emissive={i % 2 === 0 ? '#22d3ee' : '#818cf8'}
            emissiveIntensity={1.2}
            transparent
            opacity={0.45 - i * 0.06}
          />
        </mesh>
      ))}
    </group>
  );
}

/* ── Main core orb ───────────────────────────────────────────────────── */
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
            emissiveIntensity={0.5}
            roughness={0.05}
            metalness={0.95}
            distort={0.35}
            speed={2}
            envMapIntensity={1.5}
          />
        </Icosahedron>
      </Float>
      <Torus ref={torusRef} args={[2.6, 0.015, 16, 100]}>
        <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={1.5} transparent opacity={0.6} />
      </Torus>
      <Torus ref={torus2Ref} args={[3.1, 0.012, 16, 100]} rotation={[Math.PI / 3, 0, 0]}>
        <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={1.2} transparent opacity={0.4} />
      </Torus>

      {/* Orbiting satellites */}
      <Satellite radius={2.2} speed={0.9} size={0.12} color="#38bdf8" tilt={0.4} />
      <Satellite radius={3.0} speed={0.55} size={0.09} color="#a78bfa" tilt={1.1} />
      <Satellite radius={3.8} speed={0.35} size={0.07} color="#34d399" tilt={0.8} />

      {/* Holographic ring-grid disc */}
      <HoloDisc />
    </group>
  );
}

export function AICore({ className }: { className?: string }) {
  return (
    <div className={className}>
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }} dpr={[1, 2]}>
        <ambientLight intensity={0.35} />
        <pointLight position={[10, 10, 10]} intensity={1.4} color="#38bdf8" />
        <pointLight position={[-10, -5, -10]} intensity={0.9} color="#22d3ee" />
        <pointLight position={[0, -8, 4]} intensity={0.5} color="#a78bfa" />
        <Environment preset="city" />
        <CoreOrb />
        <ParticleField count={3000} />
      </Canvas>
    </div>
  );
}
