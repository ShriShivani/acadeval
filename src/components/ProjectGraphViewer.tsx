import React, { useEffect, useRef, useState, useMemo } from 'react';
import {
  Share2, Search, Filter, RefreshCw, ZoomIn, ZoomOut, Maximize2,
  Info, CheckCircle2, ChevronRight, Cpu, Database, Code, ShieldCheck, Tag
} from 'lucide-react';

export interface GraphNodeData {
  id: number | string;
  name: string;
  type: string;
  degree?: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface GraphLinkData {
  source: number | string;
  target: number | string;
  relationship: string;
  confidence?: number;
}

interface ProjectGraphViewerProps {
  nodes: GraphNodeData[];
  links: GraphLinkData[];
  onNodeClick?: (node: GraphNodeData) => void;
  isLoading?: boolean;
  onRefresh?: () => void;
}

const TYPE_COLORS: Record<string, { bg: string; text: string; border: string; colorHex: string }> = {
  Project:     { bg: 'bg-indigo-900/60', text: 'text-indigo-200', border: 'border-indigo-500', colorHex: '#6366f1' },
  Domain:      { bg: 'bg-purple-900/60', text: 'text-purple-200', border: 'border-purple-500', colorHex: '#a855f7' },
  Subdomain:   { bg: 'bg-fuchsia-900/60', text: 'text-fuchsia-200', border: 'border-fuchsia-500', colorHex: '#d946ef' },
  Algorithm:   { bg: 'bg-cyan-900/60',   text: 'text-cyan-200',   border: 'border-cyan-500',   colorHex: '#06b6d4' },
  Technology:  { bg: 'bg-emerald-900/60',text: 'text-emerald-200',border: 'border-emerald-500',colorHex: '#10b981' },
  Framework:   { bg: 'bg-teal-900/60',   text: 'text-teal-200',   border: 'border-teal-500',   colorHex: '#14b8a6' },
  Library:     { bg: 'bg-sky-900/60',    text: 'text-sky-200',    border: 'border-sky-500',    colorHex: '#0ea5e9' },
  Dataset:     { bg: 'bg-amber-900/60',  text: 'text-amber-200',  border: 'border-amber-500',  colorHex: '#f59e0b' },
  Application: { bg: 'bg-rose-900/60',   text: 'text-rose-200',   border: 'border-rose-500',   colorHex: '#f43f5e' },
  Hardware:    { bg: 'bg-pink-900/60',   text: 'text-pink-200',   border: 'border-pink-500',   colorHex: '#ec4899' },
  Metric:      { bg: 'bg-slate-800',      text: 'text-slate-200',  border: 'border-slate-500',  colorHex: '#94a3b8' },
};

const ALL_NODE_TYPES = [
  'Project', 'Domain', 'Algorithm', 'Technology',
  'Framework', 'Library', 'Dataset', 'Application', 'Hardware', 'Metric'
];

export const ProjectGraphViewer: React.FC<ProjectGraphViewerProps> = ({
  nodes,
  links,
  onNodeClick,
  isLoading = false,
  onRefresh,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [selectedNode, setSelectedNode] = useState<GraphNodeData | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTypes, setActiveTypes] = useState<Set<string>>(new Set(ALL_NODE_TYPES));
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Filter nodes & links based on active types
  const filteredNodes = useMemo(() => {
    return nodes.filter(n => activeTypes.has(n.type));
  }, [nodes, activeTypes]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes]);

  const filteredLinks = useMemo(() => {
    return links.filter(l => filteredNodeIds.has(l.source) && filteredNodeIds.has(l.target));
  }, [links, filteredNodeIds]);

  // Simple force simulation calculation in 2D space
  const simulationNodesRef = useRef<Map<string | number, GraphNodeData>>(new Map());

  useEffect(() => {
    const simMap = simulationNodesRef.current;
    const width = containerRef.current?.clientWidth || 800;
    const height = containerRef.current?.clientHeight || 600;

    // Initialize positions if new
    filteredNodes.forEach((node, i) => {
      if (!simMap.has(node.id)) {
        const angle = (i / Math.max(1, filteredNodes.length)) * 2 * Math.PI;
        const radius = Math.min(width, height) * 0.3 * Math.sqrt(Math.random());
        simMap.set(node.id, {
          ...node,
          x: width / 2 + radius * Math.cos(angle),
          y: height / 2 + radius * Math.sin(angle),
          vx: 0,
          vy: 0,
        });
      } else {
        const existing = simMap.get(node.id)!;
        existing.name = node.name;
        existing.type = node.type;
        existing.degree = node.degree;
      }
    });

    let animationFrameId: number;
    let ticks = 0;
    const maxTicks = 120;

    const runSimulationStep = () => {
      if (ticks >= maxTicks) return;
      ticks++;

      const nodeList = Array.from(simMap.values());
      const k = Math.sqrt((width * height) / Math.max(1, nodeList.length)) * 0.8;

      // 1. Repulsion between nodes
      for (let i = 0; i < nodeList.length; i++) {
        for (let j = i + 1; j < nodeList.length; j++) {
          const n1 = nodeList[i];
          const n2 = nodeList[j];
          let dx = (n2.x || 0) - (n1.x || 0);
          let dy = (n2.y || 0) - (n1.y || 0);
          let dist = Math.sqrt(dx * dx + dy * dy) || 1;
          if (dist < 200) {
            let force = (k * k) / dist;
            let fx = (dx / dist) * force * 0.05;
            let fy = (dy / dist) * force * 0.05;
            n1.vx = (n1.vx || 0) - fx;
            n1.vy = (n1.vy || 0) - fy;
            n2.vx = (n2.vx || 0) + fx;
            n2.vy = (n2.vy || 0) + fy;
          }
        }
      }

      // 2. Attraction along links
      filteredLinks.forEach(link => {
        const source = simMap.get(link.source);
        const target = simMap.get(link.target);
        if (source && target) {
          let dx = (target.x || 0) - (source.x || 0);
          let dy = (target.y || 0) - (source.y || 0);
          let dist = Math.sqrt(dx * dx + dy * dy) || 1;
          let force = (dist - k) * 0.05;
          let fx = (dx / dist) * force;
          let fy = (dy / dist) * force;
          source.vx = (source.vx || 0) + fx;
          source.vy = (source.vy || 0) + fy;
          target.vx = (target.vx || 0) - fx;
          target.vy = (target.vy || 0) - fy;
        }
      });

      // 3. Center gravity
      nodeList.forEach(n => {
        let dx = width / 2 - (n.x || 0);
        let dy = height / 2 - (n.y || 0);
        n.vx = (n.vx || 0) + dx * 0.005;
        n.vy = (n.vy || 0) + dy * 0.005;

        // Apply velocity with damping
        n.x = (n.x || 0) + (n.vx || 0) * 0.4;
        n.y = (n.y || 0) + (n.vy || 0) * 0.4;
        n.vx = (n.vx || 0) * 0.85;
        n.vy = (n.vy || 0) * 0.85;
      });

      renderCanvas();
      animationFrameId = requestAnimationFrame(runSimulationStep);
    };

    runSimulationStep();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [filteredNodes, filteredLinks]);

  // Canvas render loop
  const renderCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    ctx.save();
    ctx.clearRect(0, 0, width, height);

    // Apply pan & zoom
    ctx.translate(panOffset.x, panOffset.y);
    ctx.scale(zoomLevel, zoomLevel);

    const simMap = simulationNodesRef.current;

    // Draw links
    filteredLinks.forEach(link => {
      const source = simMap.get(link.source);
      const target = simMap.get(link.target);
      if (source && target && source.x && source.y && target.x && target.y) {
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle = link.relationship === 'CO_OCCURS' ? 'rgba(148, 163, 184, 0.25)' : 'rgba(99, 102, 241, 0.4)';
        ctx.lineWidth = link.relationship === 'CO_OCCURS' ? 1 : 1.5;
        ctx.stroke();
      }
    });

    // Draw nodes
    const lowerSearch = searchTerm.trim().toLowerCase();

    Array.from(simMap.values()).forEach(node => {
      if (!node.x || !node.y) return;

      const isMatchingSearch = lowerSearch.length > 0 && node.name.toLowerCase().includes(lowerSearch);
      const isSelected = selectedNode?.id === node.id;
      const typeStyle = TYPE_COLORS[node.type] || TYPE_COLORS['Metric'];

      const radius = node.type === 'Project' ? 14 : Math.min(12, 6 + (node.degree || 1));

      // Outer glow for search match or selected
      if (isSelected || isMatchingSearch) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius + 6, 0, 2 * Math.PI);
        ctx.fillStyle = isSelected ? 'rgba(99, 102, 241, 0.35)' : 'rgba(234, 179, 8, 0.35)';
        ctx.fill();
      }

      // Main Circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
      ctx.fillStyle = typeStyle.colorHex;
      ctx.fill();
      ctx.lineWidth = isSelected ? 3 : 1.5;
      ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(255, 255, 255, 0.6)';
      ctx.stroke();

      // Node Label
      ctx.font = isSelected ? 'bold 12px Inter, sans-serif' : '10px Inter, sans-serif';
      ctx.fillStyle = isSelected || isMatchingSearch ? '#ffffff' : 'rgba(226, 232, 240, 0.85)';
      ctx.textAlign = 'center';
      ctx.fillText(node.name.length > 18 ? node.name.substring(0, 16) + '…' : node.name, node.x, node.y + radius + 14);
    });

    ctx.restore();
  };

  // Canvas resize listener
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current && canvasRef.current) {
        canvasRef.current.width = containerRef.current.clientWidth;
        canvasRef.current.height = containerRef.current.clientHeight;
        renderCanvas();
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle canvas click to select node
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const clickX = (e.clientX - rect.left - panOffset.x) / zoomLevel;
    const clickY = (e.clientY - rect.top - panOffset.y) / zoomLevel;

    const simMap = simulationNodesRef.current;
    let clickedNode: GraphNodeData | null = null;

    Array.from(simMap.values()).forEach(node => {
      if (node.x && node.y) {
        const radius = node.type === 'Project' ? 14 : 10;
        const dist = Math.sqrt((clickX - node.x) ** 2 + (clickY - node.y) ** 2);
        if (dist <= radius + 5) {
          clickedNode = node;
        }
      }
    });

    setSelectedNode(clickedNode);
    if (clickedNode && onNodeClick) {
      onNodeClick(clickedNode);
    }
  };

  // Pan controls
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPanOffset({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
      renderCanvas();
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const toggleTypeFilter = (type: string) => {
    setActiveTypes(prev => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  };

  // Selected node neighbors
  const connectedLinks = useMemo(() => {
    if (!selectedNode) return [];
    return links.filter(l => l.source === selectedNode.id || l.target === selectedNode.id);
  }, [selectedNode, links]);

  return (
    <div className="flex flex-col lg:flex-row gap-4 h-[720px] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
      {/* Main Canvas Graph Viewer */}
      <div ref={containerRef} className="relative flex-1 bg-slate-950/80 overflow-hidden cursor-grab active:cursor-grabbing">
        {/* Top Control Bar */}
        <div className="absolute top-4 left-4 right-4 z-10 flex flex-wrap items-center justify-between gap-3 bg-slate-900/90 backdrop-blur-md p-3 rounded-xl border border-slate-800 shadow-lg">
          {/* Search Box */}
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search graph node..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950 text-slate-100 pl-9 pr-4 py-1.5 rounded-lg border border-slate-700 text-xs focus:outline-none focus:border-indigo-500 transition"
            />
          </div>

          {/* Quick Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setZoomLevel(z => Math.min(z + 0.25, 2.5))}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => setZoomLevel(z => Math.max(z - 0.25, 0.4))}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => { setZoomLevel(1); setPanOffset({ x: 0, y: 0 }); }}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition"
              title="Reset View"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="p-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition flex items-center gap-1 text-xs px-2.5 font-medium"
                title="Refresh Graph Data"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Reload
              </button>
            )}
          </div>
        </div>

        {/* Category Filter Badges Bar */}
        <div className="absolute bottom-4 left-4 right-4 z-10 flex flex-wrap items-center gap-1.5 bg-slate-900/90 backdrop-blur-md p-2.5 rounded-xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mr-2 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Filters:
          </span>
          {ALL_NODE_TYPES.map(type => {
            const isActive = activeTypes.has(type);
            const style = TYPE_COLORS[type];
            return (
              <button
                key={type}
                onClick={() => toggleTypeFilter(type)}
                className={`text-[10px] font-medium px-2.5 py-1 rounded-md border transition flex items-center gap-1 ${
                  isActive
                    ? `${style.bg} ${style.text} ${style.border}`
                    : 'bg-slate-950/60 text-slate-500 border-slate-800 opacity-60 hover:opacity-100'
                }`}
              >
                <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: style.colorHex }} />
                {type}
              </button>
            );
          })}
        </div>

        {/* Interactive Canvas */}
        <canvas
          ref={canvasRef}
          onClick={handleCanvasClick}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className="w-full h-full"
        />

        {isLoading && (
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-20">
            <div className="flex flex-col items-center gap-3">
              <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
              <p className="text-sm font-medium text-slate-300">Constructing Knowledge Graph...</p>
            </div>
          </div>
        )}
      </div>

      {/* Side Inspector Drawer */}
      <div className="w-full lg:w-80 bg-slate-900 border-t lg:border-t-0 lg:border-l border-slate-800 p-5 flex flex-col justify-between overflow-y-auto">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 mb-4 font-semibold text-sm">
            <Share2 className="w-4 h-4" /> Node Inspector
          </div>

          {selectedNode ? (
            <div className="space-y-4">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <span className={`inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border mb-2 ${TYPE_COLORS[selectedNode.type]?.bg} ${TYPE_COLORS[selectedNode.type]?.text} ${TYPE_COLORS[selectedNode.type]?.border}`}>
                  {selectedNode.type}
                </span>
                <h4 className="text-base font-bold text-slate-100 leading-snug">{selectedNode.name}</h4>
                <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-slate-500" /> ID: <span className="font-mono text-slate-300">{selectedNode.id}</span>
                </p>
                <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <span className="text-slate-400">Degree Connections:</span>
                  <span className="font-bold text-indigo-300 bg-indigo-950 px-2 py-0.5 rounded border border-indigo-800">
                    {selectedNode.degree || connectedLinks.length} edges
                  </span>
                </div>
              </div>

              {/* Connected Links List */}
              <div>
                <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Connected Neighborhood ({connectedLinks.length})</h5>
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {connectedLinks.length > 0 ? (
                    connectedLinks.map((link, idx) => {
                      const otherId = link.source === selectedNode.id ? link.target : link.source;
                      const otherNode = nodes.find(n => n.id === otherId);
                      return (
                        <div key={idx} className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 text-xs flex items-center justify-between">
                          <div>
                            <span className="text-[10px] text-slate-400 block font-mono uppercase">{link.relationship}</span>
                            <span className="font-medium text-slate-200">{otherNode?.name || otherId}</span>
                          </div>
                          <span className={`text-[9px] px-1.5 py-0.5 rounded border ${TYPE_COLORS[otherNode?.type || '']?.bg || 'bg-slate-800'} ${TYPE_COLORS[otherNode?.type || '']?.text || 'text-slate-300'}`}>
                            {otherNode?.type || 'Node'}
                          </span>
                        </div>
                      );
                    })
                  ) : (
                    <p className="text-xs text-slate-500 italic">No connected links in current view.</p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-950/60 p-6 rounded-xl border border-slate-800 text-center text-slate-400 text-xs space-y-3">
              <Info className="w-8 h-8 text-slate-600 mx-auto" />
              <p className="font-medium text-slate-300">Click any node in the graph viewer to inspect its connections and structural metrics.</p>
              <div className="pt-2 text-[11px] text-slate-500 space-y-1 text-left">
                <p>💡 <b>Tip:</b> Scroll/drag to pan the graph layout.</p>
                <p>💡 <b>Tip:</b> Filter categories using the bottom bar.</p>
              </div>
            </div>
          )}
        </div>

        {/* Legend Footer */}
        <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
          <span>AcadEval+ Module 4</span>
          <span className="font-mono text-slate-400">NetworkX MultiDiGraph</span>
        </div>
      </div>
    </div>
  );
};
