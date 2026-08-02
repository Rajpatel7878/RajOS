'use client';

import { useRef, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { knowledgeNodes, knowledgeEdges } from '@/lib/data';
import type { KnowledgeNode } from '@/lib/types';
import { cn } from '@/lib/utils';

const groupColors: Record<KnowledgeNode['group'], string> = {
  core: '#38bdf8',
  domain: '#22d3ee',
  document: '#34d399',
  concept: '#a78bfa',
};

const groupSizes: Record<KnowledgeNode['group'], number> = {
  core: 30,
  domain: 20,
  document: 14,
  concept: 10,
};

interface PositionedNode extends KnowledgeNode {
  x: number;
  y: number;
}

export function KnowledgeGraph({ className }: { className?: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>('n0');

  const nodes = useMemo<PositionedNode[]>(() => {
    const cx = 300;
    const cy = 250;
    return knowledgeNodes.map((node, i) => {
      if (node.group === 'core') {
        return { ...node, x: cx, y: cy };
      }
      if (node.group === 'domain') {
        const angle = (i / 5) * Math.PI * 2 - Math.PI / 2;
        return { ...node, x: cx + Math.cos(angle) * 120, y: cy + Math.sin(angle) * 120 };
      }
      if (node.group === 'document') {
        const angle = (i / 6) * Math.PI * 2 + 0.3;
        return { ...node, x: cx + Math.cos(angle) * 210, y: cy + Math.sin(angle) * 210 };
      }
      const angle = (i / 6) * Math.PI * 2 + 1.5;
      return { ...node, x: cx + Math.cos(angle) * 270, y: cy + Math.sin(angle) * 270 + 40 };
    });
  }, []);

  const nodeMap = useMemo(() => {
    const map: Record<string, PositionedNode> = {};
    nodes.forEach((n) => { map[n.id] = n; });
    return map;
  }, [nodes]);

  const connectedEdges = useMemo(() => {
    if (!hovered && !selected) return knowledgeEdges;
    const id = hovered ?? selected;
    return knowledgeEdges.filter((e) => e.source === id || e.target === id);
  }, [hovered, selected]);

  const selectedNode = selected ? nodeMap[selected] : null;

  return (
    <div ref={containerRef} className={cn('relative overflow-hidden', className)}>
      <svg viewBox="0 0 600 500" className="h-full w-full">
        {/* edges */}
        {knowledgeEdges.map((edge, i) => {
          const source = nodeMap[edge.source];
          const target = nodeMap[edge.target];
          if (!source || !target) return null;
          const isActive = connectedEdges.includes(edge);
          return (
            <line
              key={i}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke={isActive ? 'rgba(56, 189, 248, 0.5)' : 'rgba(255,255,255,0.06)'}
              strokeWidth={isActive ? 1.5 : 1}
              strokeDasharray={isActive ? '0' : '4 4'}
            >
              <animate
                attributeName="stroke-dashoffset"
                values="0;-8"
                dur="2s"
                repeatCount="indefinite"
              />
            </line>
          );
        })}

        {/* nodes */}
        {nodes.map((node) => {
          const r = groupSizes[node.group];
          const color = groupColors[node.group];
          const isHovered = hovered === node.id;
          const isSelected = selected === node.id;
          const isConnected = connectedEdges.some(
            (e) => e.source === node.id || e.target === node.id
          );

          return (
            <g
              key={node.id}
              transform={`translate(${node.x}, ${node.y})`}
              className="cursor-pointer"
              onMouseEnter={() => setHovered(node.id)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => setSelected(node.id)}
            >
              {(isHovered || isSelected) && (
                <circle r={r + 8} fill={color} opacity={0.15}>
                  <animate attributeName="r" values={`${r + 6};${r + 12};${r + 6}`} dur="2s" repeatCount="indefinite" />
                </circle>
              )}
              <circle
                r={r}
                fill={color}
                opacity={isConnected || isHovered || isSelected ? 0.9 : 0.4}
                fillOpacity={isConnected || isHovered || isSelected ? 0.2 : 0.1}
                stroke={color}
                strokeWidth={isSelected ? 2.5 : 1.5}
              />
              {node.group === 'core' && (
                <circle r={r - 8} fill={color} opacity={0.8}>
                  <animate attributeName="opacity" values="0.4;0.9;0.4" dur="3s" repeatCount="indefinite" />
                </circle>
              )}
              <text
                y={r + 14}
                textAnchor="middle"
                className="fill-white/70 text-[10px] font-medium"
                style={{ pointerEvents: 'none', opacity: isHovered || isSelected ? 1 : 0.6 }}
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Selected node info */}
      {selectedNode && (
        <motion.div
          key={selectedNode.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute bottom-4 left-4 rounded-xl border border-white/10 bg-black/60 p-4 backdrop-blur-xl"
        >
          <div className="flex items-center gap-2">
            <span
              className="h-3 w-3 rounded-full"
              style={{ background: groupColors[selectedNode.group] }}
            />
            <span className="text-sm font-semibold text-white">{selectedNode.label}</span>
          </div>
          <p className="mt-1 text-xs capitalize text-muted-foreground">{selectedNode.group} node</p>
          <p className="mt-2 text-xs text-muted-foreground">
            {connectedEdges.length} connections
          </p>
        </motion.div>
      )}

      {/* Legend */}
      <div className="absolute right-4 top-4 space-y-2 rounded-xl border border-white/10 bg-black/40 p-3 backdrop-blur-xl">
        {Object.entries(groupColors).map(([group, color]) => (
          <div key={group} className="flex items-center gap-2 text-xs">
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: color }} />
            <span className="capitalize text-muted-foreground">{group}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
