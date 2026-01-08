"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { GraphData, GraphNode, GraphEdge } from "@/types";

interface MemoryGraphProps {
  data: GraphData;
  width?: number;
  height?: number;
}

export default function MemoryGraph({ data, width = 800, height = 600 }: MemoryGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const simulation = d3.forceSimulation<any>(data.nodes)
      .force("link", d3.forceLink<any, any>(data.edges).id((d) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const g = svg.append("g");

    // Add zoom behavior
    svg.call(d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      }));

    // Draw edges
    const link = g.append("g")
      .attr("stroke", "#334155")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(data.edges)
      .join("line")
      .attr("stroke-width", (d) => Math.sqrt(d.weight || 1) * 2);

    // Draw nodes
    const node = g.append("g")
      .selectAll("g")
      .data(data.nodes)
      .join("g")
      .call(drag(simulation) as any);

    // Node circles
    node.append("circle")
      .attr("r", (d) => d.type === 'Entity' ? 12 : 8)
      .attr("fill", (d) => {
        switch (d.type) {
          case 'Entity': return '#60a5fa'; // blue-400
          case 'Experience': return '#818cf8'; // indigo-400
          case 'Context': return '#fbbf24'; // amber-400
          default: return '#94a3b8';
        }
      })
      .attr("stroke", "#1e293b")
      .attr("stroke-width", 2);

    // Node labels
    node.append("text")
      .text((d) => d.label)
      .attr("x", 15)
      .attr("y", 5)
      .attr("fill", "#f8fafc")
      .style("font-size", "10px")
      .style("pointer-events", "none")
      .style("text-shadow", "0 1px 2px rgba(0,0,0,0.8)");

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    function drag(simulation: d3.Simulation<any, undefined>) {
      function dragstarted(event: any) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event: any) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event: any) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }

    return () => {
      simulation.stop();
    };
  }, [data, width, height]);

  return (
    <div className="relative w-full h-full bg-slate-950 rounded-xl overflow-hidden border border-slate-800">
      <svg 
        ref={svgRef} 
        width="100%" 
        height="100%" 
        viewBox={`0 0 ${width} ${height}`}
        className="cursor-move"
      />
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 p-3 bg-slate-900/80 backdrop-blur-sm border border-slate-800 rounded-lg space-y-2">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-400" />
          <span className="text-[10px] uppercase font-bold text-slate-400">Entity</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-indigo-400" />
          <span className="text-[10px] uppercase font-bold text-slate-400">Experience</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-amber-400" />
          <span className="text-[10px] uppercase font-bold text-slate-400">Context</span>
        </div>
      </div>
    </div>
  );
}

