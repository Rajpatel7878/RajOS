"use client";

import { useRef, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, Float, Text, Line, Html } from "@react-three/drei";
import * as THREE from "three";
import { knowledgeNodes, knowledgeEdges } from "@/lib/data";
import type { KnowledgeNode } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Sparkles, Layers, Box, Maximize2, Orbit } from "lucide-react";

const groupColors: Record<KnowledgeNode["group"], string> = {
  core: "#38bdf8",
  domain: "#22d3ee",
  document: "#34d399",
  concept: "#a78bfa",
};

interface Spatial3DNode extends KnowledgeNode {
  position: [number, number, number];
}

// ── 3D Scene Inside Canvas ──
function SpatialGraphScene({
  selectedId,
  hoveredId,
  onSelectNode,
  onHoverNode,
}: {
  selectedId: string | null;
  hoveredId: string | null;
  onSelectNode: (id: string) => void;
  onHoverNode: (id: string | null) => void;
}) {
  const groupRef = useRef<THREE.Group>(null);

  // Position nodes in 3D sphere volume
  const nodes3D: Spatial3DNode[] = useMemo(() => {
    return knowledgeNodes.map((node, i) => {
      if (node.group === "core") {
        return { ...node, position: [0, 0, 0] };
      }
      if (node.group === "domain") {
        const phi = Math.PI * (3 - Math.sqrt(5)) * i;
        const y = 1 - (i / 4) * 2;
        const radius = Math.sqrt(1 - y * y) * 2.8;
        return {
          ...node,
          position: [Math.cos(phi) * radius, y * 1.5, Math.sin(phi) * radius],
        };
      }
      if (node.group === "document") {
        const angle = (i / 6) * Math.PI * 2;
        return {
          ...node,
          position: [Math.cos(angle) * 4.2, Math.sin(i * 1.5) * 1.8, Math.sin(angle) * 4.2],
        };
      }
      // Concepts
      const angle = (i / 8) * Math.PI * 2 + 1.2;
      return {
        ...node,
        position: [Math.cos(angle) * 5.4, Math.sin(angle) * 2.5, (Math.random() - 0.5) * 3],
      };
    });
  }, []);

  const nodeMap = useMemo(() => {
    const map = new Map<string, Spatial3DNode>();
    nodes3D.forEach((n) => map.set(n.id, n));
    return map;
  }, [nodes3D]);

  // Slow ambient spatial drift
  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime;
    groupRef.current.rotation.y = t * 0.04;
    groupRef.current.rotation.x = Math.sin(t * 0.08) * 0.05;
  });

  return (
    <group ref={groupRef}>
      {/* 3D Inter-Node Connection Lines */}
      {knowledgeEdges.map((edge, idx) => {
        const src = nodeMap.get(edge.source);
        const tgt = nodeMap.get(edge.target);
        if (!src || !tgt) return null;

        const isHighlighted =
          selectedId === edge.source ||
          selectedId === edge.target ||
          hoveredId === edge.source ||
          hoveredId === edge.target;

        return (
          <Line
            key={idx}
            points={[src.position, tgt.position]}
            color={isHighlighted ? "#38bdf8" : "rgba(255,255,255,0.12)"}
            lineWidth={isHighlighted ? 2 : 0.8}
            transparent
            opacity={isHighlighted ? 0.9 : 0.25}
          />
        );
      })}

      {/* 3D Nodes */}
      {nodes3D.map((node) => {
        const isCore = node.group === "core";
        const isSelected = selectedId === node.id;
        const isHovered = hoveredId === node.id;
        const color = groupColors[node.group];
        const radius = isCore ? 0.45 : node.group === "domain" ? 0.3 : node.group === "document" ? 0.22 : 0.16;

        return (
          <Float key={node.id} speed={2} rotationIntensity={0.2} floatIntensity={0.3}>
            <group position={node.position}>
              <Sphere
                args={[radius * (isSelected || isHovered ? 1.3 : 1), 32, 32]}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectNode(node.id);
                }}
                onPointerOver={(e) => {
                  e.stopPropagation();
                  onHoverNode(node.id);
                }}
                onPointerOut={() => onHoverNode(null)}
              >
                <meshStandardMaterial
                  color={color}
                  emissive={color}
                  emissiveIntensity={isSelected || isHovered ? 1.8 : 0.6}
                  roughness={0.15}
                  metalness={0.85}
                />
              </Sphere>

              {/* Halo ring around selected or hovered node */}
              {(isSelected || isHovered) && (
                <mesh>
                  <ringGeometry args={[radius * 1.5, radius * 1.7, 32]} />
                  <meshBasicMaterial color={color} side={THREE.DoubleSide} transparent opacity={0.7} />
                </mesh>
              )}

              {/* Node Label in 3D */}
              <Text
                position={[0, radius + 0.35, 0]}
                fontSize={0.22}
                color={isSelected || isHovered ? "#ffffff" : "rgba(255,255,255,0.65)"}
                anchorX="center"
                anchorY="middle"
              >
                {node.label}
              </Text>
            </group>
          </Float>
        );
      })}
    </group>
  );
}

// ── Main KnowledgeGraph Component ──
export function KnowledgeGraph({ className }: { className?: string }) {
  const [selectedId, setSelectedId] = useState<string | null>("n0");
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"3D" | "2D">("3D");

  const selectedNode = useMemo(() => {
    return knowledgeNodes.find((n) => n.id === selectedId) ?? null;
  }, [selectedId]);

  const connectedEdgesCount = useMemo(() => {
    if (!selectedId) return 0;
    return knowledgeEdges.filter((e) => e.source === selectedId || e.target === selectedId).length;
  }, [selectedId]);

  return (
    <div className={cn("relative h-[520px] w-full overflow-hidden rounded-3xl border border-white/[0.08] bg-black/50 backdrop-blur-2xl shadow-[0_20px_50px_rgba(0,0,0,0.7)]", className)}>
      {/* 3D Vignette Background Lights */}
      <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-sky-500/15 blur-3xl" />
      <div className="pointer-events-none absolute -right-20 -bottom-20 h-64 w-64 rounded-full bg-violet-500/15 blur-3xl" />
      <div className="pointer-events-none absolute inset-0 scanlines opacity-30" />

      {/* ── View Controls Bar ── */}
      <div className="absolute left-5 top-5 z-20 flex items-center gap-2">
        <div className="flex items-center gap-1.5 rounded-xl border border-white/10 bg-black/60 p-1 backdrop-blur-xl">
          <button
            onClick={() => setViewMode("3D")}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold transition-all",
              viewMode === "3D"
                ? "bg-gradient-to-r from-sky-500 to-cyan-400 text-white shadow-md"
                : "text-muted-foreground hover:text-white"
            )}
          >
            <Orbit className="h-3.5 w-3.5" />
            3D Universe
          </button>
          <button
            onClick={() => setViewMode("2D")}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold transition-all",
              viewMode === "2D"
                ? "bg-gradient-to-r from-sky-500 to-cyan-400 text-white shadow-md"
                : "text-muted-foreground hover:text-white"
            )}
          >
            <Layers className="h-3.5 w-3.5" />
            Planar Web
          </button>
        </div>
      </div>

      {/* ── Legend ── */}
      <div className="absolute right-5 top-5 z-20 hidden sm:flex items-center gap-3 rounded-2xl border border-white/10 bg-black/60 px-3.5 py-2 backdrop-blur-xl">
        {Object.entries(groupColors).map(([group, color]) => (
          <div key={group} className="flex items-center gap-1.5 text-xs">
            <span className="h-2 w-2 rounded-full shadow-[0_0_6px]" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
            <span className="capitalize text-muted-foreground text-[11px] font-medium">{group}</span>
          </div>
        ))}
      </div>

      {/* ── 3D Viewport ── */}
      {viewMode === "3D" ? (
        <div className="h-full w-full cursor-grab active:cursor-grabbing">
          <Canvas camera={{ position: [0, 1, 9], fov: 48 }} dpr={[1, 2]}>
            <ambientLight intensity={0.4} />
            <pointLight position={[10, 10, 10]} intensity={1.5} color="#38bdf8" />
            <pointLight position={[-10, -10, -10]} intensity={1.0} color="#a78bfa" />
            <SpatialGraphScene
              selectedId={selectedId}
              hoveredId={hoveredId}
              onSelectNode={setSelectedId}
              onHoverNode={setHoveredId}
            />
          </Canvas>
        </div>
      ) : (
        /* 2D Topological SVG Mode */
        <div className="h-full w-full p-8 flex items-center justify-center">
          <svg viewBox="0 0 600 420" className="h-full w-full max-w-2xl">
            {knowledgeEdges.map((edge, i) => {
              const srcIdx = knowledgeNodes.findIndex((n) => n.id === edge.source);
              const tgtIdx = knowledgeNodes.findIndex((n) => n.id === edge.target);
              const x1 = 300 + Math.cos(srcIdx * 0.8) * 160;
              const y1 = 210 + Math.sin(srcIdx * 0.8) * 120;
              const x2 = 300 + Math.cos(tgtIdx * 0.8) * 160;
              const y2 = 210 + Math.sin(tgtIdx * 0.8) * 120;
              const isActive = selectedId === edge.source || selectedId === edge.target;

              return (
                <line
                  key={i}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={isActive ? "#38bdf8" : "rgba(255,255,255,0.08)"}
                  strokeWidth={isActive ? 2 : 1}
                />
              );
            })}
            {knowledgeNodes.map((node, i) => {
              const x = node.group === "core" ? 300 : 300 + Math.cos(i * 0.8) * 160;
              const y = node.group === "core" ? 210 : 210 + Math.sin(i * 0.8) * 120;
              const color = groupColors[node.group];
              const isSelected = selectedId === node.id;

              return (
                <g key={node.id} onClick={() => setSelectedId(node.id)} className="cursor-pointer">
                  <circle
                    cx={x}
                    cy={y}
                    r={isSelected ? 16 : 10}
                    fill={color}
                    stroke="#ffffff"
                    strokeWidth={isSelected ? 2 : 0}
                    opacity={isSelected ? 1 : 0.75}
                  />
                  <text x={x} y={y + 22} textAnchor="middle" fill="#ffffff" fontSize="10">
                    {node.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      )}

      {/* ── Holographic Node Inspector Card ── */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.95 }}
            className="absolute bottom-5 left-5 z-20 max-w-sm rounded-2xl border border-white/15 bg-black/80 p-4.5 backdrop-blur-2xl shadow-[0_16px_36px_rgba(0,0,0,0.8)]"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span
                  className="h-3.5 w-3.5 rounded-full"
                  style={{
                    background: groupColors[selectedNode.group],
                    boxShadow: `0 0 10px ${groupColors[selectedNode.group]}`,
                  }}
                />
                <h4 className="text-sm font-bold text-white tracking-tight">{selectedNode.label}</h4>
              </div>
              <span className="rounded-md bg-white/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-sky-300">
                {selectedNode.group}
              </span>
            </div>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Indexed semantic intelligence node with {connectedEdgesCount} dynamic cross-references.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
