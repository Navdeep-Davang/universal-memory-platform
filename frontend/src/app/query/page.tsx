"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { MemoryResult } from "@/types";
import { 
  Search, 
  Send, 
  Cpu, 
  Database, 
  Clock, 
  Info,
  ChevronRight,
  Filter,
  Loader2
} from "lucide-react";

export default function QueryPage() {
  const [query, setQuery] = useState("");
  const [agentId, setAgentId] = useState("agent-001");
  const [limit, setLimit] = useState(10);
  const [results, setResults] = useState<MemoryResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await api.queryMemories(query, agentId, limit);
      setResults(data.results || []);
    } catch (err: any) {
      setError(err.message || "Failed to execute query");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <header>
        <h2 className="text-3xl font-bold tracking-tight">Query Playbox</h2>
        <p className="text-slate-400 mt-2">Test the memory engine's recall and retrieval performance.</p>
      </header>

      {/* Query Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <form onSubmit={handleQuery} className="space-y-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
              <input 
                type="text" 
                placeholder="What does the user prefer for dinner?"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-12 pr-4 py-4 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all placeholder:text-slate-600"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button 
              type="submit"
              disabled={loading || !query.trim()}
              className="px-8 py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-xl font-bold transition-all flex items-center justify-center gap-2 min-w-[140px]"
            >
              {loading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
              Execute
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-6 pt-2">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Agent ID</span>
              <input 
                type="text" 
                className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={agentId}
                onChange={(e) => setAgentId(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Result Limit</span>
              <select 
                className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 p-4 rounded-xl text-red-400 flex items-center gap-3">
          <Info size={20} />
          <p>{error}</p>
        </div>
      )}

      {/* Results Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            Recall Results
            <span className="bg-slate-800 text-slate-400 text-xs px-2 py-0.5 rounded-full font-normal">
              {results.length} found
            </span>
          </h3>
          <div className="flex gap-2">
            <button className="p-1.5 text-slate-500 hover:text-white transition-colors">
              <Filter size={18} />
            </button>
          </div>
        </div>

        {results.length === 0 && !loading && !error && (
          <div className="bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl p-20 text-center">
            <div className="w-16 h-16 bg-slate-900 border border-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-600">
              <Search size={32} />
            </div>
            <h4 className="text-slate-400 font-medium">No results to display</h4>
            <p className="text-slate-600 text-sm mt-1">Enter a query above to search memories.</p>
          </div>
        )}

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl h-32 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {results.map((result, i) => (
              <div key={result.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-blue-500/50 transition-colors group">
                <div className="p-5 flex gap-5">
                  <div className="flex flex-col items-center justify-center w-16 gap-1 border-r border-slate-800 pr-5">
                    <span className="text-[10px] font-bold text-slate-500 uppercase">Score</span>
                    <span className="text-lg font-bold text-blue-400">{(result.score * 100).toFixed(0)}</span>
                  </div>
                  
                  <div className="flex-1 space-y-3">
                    <p className="text-slate-200 leading-relaxed">
                      "{result.content}"
                    </p>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                      <div className="flex items-center gap-1.5 text-xs text-slate-500">
                        <Database size={12} />
                        <span className="font-mono">{result.id.substring(0, 8)}...</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-slate-500">
                        <Clock size={12} />
                        <span>{new Date(result.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-slate-500">
                        <Cpu size={12} />
                        <span>{result.metadata.memory_type || "Episodic"}</span>
                      </div>
                    </div>
                  </div>
                  
                  <button className="self-center p-2 text-slate-600 group-hover:text-blue-400 transition-colors">
                    <ChevronRight size={20} />
                  </button>
                </div>
                
                {/* Expandable metadata preview (simplified for now) */}
                <div className="px-5 py-3 bg-slate-950/50 border-t border-slate-800 flex flex-wrap gap-2">
                  {Object.entries(result.metadata).slice(0, 3).map(([key, val]) => (
                    <span key={key} className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded uppercase tracking-tighter">
                      {key}: {String(val)}
                    </span>
                  ))}
                  {Object.keys(result.metadata).length > 3 && (
                    <span className="text-[10px] text-slate-600 px-2 py-0.5">+{Object.keys(result.metadata).length - 3} more</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

