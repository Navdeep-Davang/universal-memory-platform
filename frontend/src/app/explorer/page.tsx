"use client";

import { useState } from "react";
import MemoryGraph from "@/components/MemoryGraph";
import { GraphData } from "@/types";
import { 
  Database, 
  Maximize2, 
  Settings2, 
  Info,
  Layers,
  Search
} from "lucide-react";

export default function ExplorerPage() {
  // Mock data for initial visualization demonstration
  const [graphData] = useState<GraphData>({
    nodes: [
      { id: "1", label: "User Preferences", type: "Entity", properties: {} },
      { id: "2", label: "Dark Mode", type: "Context", properties: {} },
      { id: "3", label: "Ingested: User likes dark mode", type: "Experience", properties: {} },
      { id: "4", label: "UI Experience", type: "Entity", properties: {} },
      { id: "5", label: "Agent Smith", type: "Entity", properties: {} },
    ],
    edges: [
      { id: "e1", source: "1", target: "2", label: "has_context", weight: 0.8 },
      { id: "e2", source: "3", target: "1", label: "about_entity", weight: 0.9 },
      { id: "e3", source: "3", target: "2", label: "contained_context", weight: 0.7 },
      { id: "e4", source: "3", target: "5", label: "recorded_by", weight: 1.0 },
      { id: "e5", source: "4", target: "1", label: "related_to", weight: 0.5 },
    ]
  });

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col space-y-6">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Graph Explorer</h2>
          <p className="text-slate-400 mt-1">Visualize and traverse the cognitive memory graph.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-300 hover:bg-slate-800 transition-colors">
            <Maximize2 size={16} />
            Full Screen
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-slate-300 hover:bg-slate-800 transition-colors">
            <Settings2 size={16} />
            Layout Settings
          </button>
        </div>
      </header>

      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Sidebar Controls */}
        <aside className="w-80 flex flex-col gap-6 overflow-y-auto pr-2">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center gap-2 text-blue-400 font-semibold text-sm uppercase tracking-wider">
              <Search size={16} />
              Search Graph
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
              <input 
                type="text" 
                placeholder="Find entity or node..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm uppercase tracking-wider">
              <Layers size={16} />
              Traversal Settings
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">K-Hop Distance</span>
                  <span className="text-slate-300 font-mono">2</span>
                </div>
                <input type="range" min="1" max="5" defaultValue="2" className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Min Edge Weight</span>
                  <span className="text-slate-300 font-mono">0.2</span>
                </div>
                <input type="range" min="0" max="1" step="0.1" defaultValue="0.2" className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500" />
              </div>
            </div>
          </div>

          <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-5 overflow-hidden flex flex-col">
            <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm uppercase tracking-wider mb-4">
              <Info size={16} />
              Node Details
            </div>
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 border border-dashed border-slate-800 rounded-lg">
              <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center text-slate-600 mb-3">
                <Database size={24} />
              </div>
              <p className="text-sm text-slate-500 italic">Select a node in the graph to view properties and provenance metadata.</p>
            </div>
          </div>
        </aside>

        {/* Main Graph View */}
        <div className="flex-1 relative">
          <MemoryGraph data={graphData} />
        </div>
      </div>
    </div>
  );
}

